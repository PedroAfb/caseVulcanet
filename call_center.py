from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ServerFactory as SvFactory
from twisted.internet.endpoints import TCP4ServerEndpoint


class Operator:
    def __init__(self, id):
        self.id = id
        self.status = "available"


ANSWERED = True
NOT_ANSWERED = False


class ServerFactory(SvFactory):
    def buildProtocol(self, addr):
        return Server()


class Server(Protocol):
    def connectionMade(self):
        print("Connection made, Server")
        self.call_center = CallCenter()

    def dataReceived(self, data):
        data = data.decode()
        data = data.split()
        command = data[0]
        if command == "call":
            msg = self.call_center.call(data[1])
        elif command == "answer":
            msg = self.call_center.answer(data[1])
        elif command == "reject":
            msg = self.call_center.reject(data[1])
        elif command == "hangup":
            msg = self.call_center.hangup(data[1])

        self.transport.write(msg.encode())


class CallCenter:
    def __init__(self, operators=[Operator("A"), Operator("B")]):
        self.operators = operators
        self.queue_calls = []
        self.active_calls = dict()

    def get_call_id(self, operator_id):
        for call_id, (_, operator) in self.active_calls.items():
            if operator.id == operator_id:
                return call_id, operator
        return None

    def verify_operators(self):
        if self.queue_calls:
            for operator in self.operators:
                if operator.status == "available":
                    call_id = self.queue_calls.pop(0)
                    operator.status = "ringing"
                    self.active_calls[call_id] = (NOT_ANSWERED, operator)
                    return (
                        "Call "
                        + call_id
                        + " ringing for operator "
                        + operator.id
                        + "\n"
                    )
        return ""

    def call(self, call_id):
        msg = "Call " + call_id + " received\n"

        for operator in self.operators:
            if operator.status == "available":
                msg += "Call " + call_id + " ringing for operator " + operator.id + "\n"
                operator.status = "ringing"
                self.active_calls[call_id] = (NOT_ANSWERED, operator)
                return msg

        self.queue_calls.append(call_id)
        msg += "Call " + call_id + " waiting in queue\n"
        return msg

    def answer(self, operator_id):
        call_id, operator = self.get_call_id(operator_id)
        self.active_calls[call_id] = (ANSWERED, operator)
        operator.status = "busy"
        msg = "Call " + call_id + " answered by operator " + operator_id + "\n"
        return msg

    def reject(self, operator_id):
        call_id, operator = self.get_call_id(operator_id)
        operator.status = "available"
        del self.active_calls[call_id]
        self.queue_calls.append(call_id)
        msg = "Call " + call_id + " rejected by operator " + operator_id + "\n"
        msg += self.verify_operators()
        return msg

    def hangup(self, call_id):
        msg = ""
        if call_id in self.active_calls and self.active_calls[call_id][0] == ANSWERED:
            _, operator = self.active_calls[call_id]
            del self.active_calls[call_id]
            operator.status = "available"
            msg = (
                "Call "
                + call_id
                + " finished and operator "
                + operator.id
                + " available\n"
            )
            msg += self.verify_operators()
            return msg
        else:
            msg = "Call " + call_id + " missed\n"
            if call_id in self.queue_calls:
                self.queue_calls.remove(call_id)

            if call_id in self.active_calls:
                _, operator = self.active_calls[call_id]
                operator.status = "available"
                del self.active_calls[call_id]
                msg += self.verify_operators()
            return msg


if __name__ == "__main__":
    endpoint = TCP4ServerEndpoint(reactor, 5678)
    endpoint.listen(ServerFactory())
    reactor.run()
