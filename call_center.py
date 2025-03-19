from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ServerFactory as SvFactory
from twisted.internet.endpoints import TCP4ServerEndpoint
import json


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
        self.call_center = CallCenter(self)

    def dataReceived(self, data):
        data_json = json.loads(data.decode())
        command = data_json["command"]
        id = data_json["id"]

        if command == "call":
            msg = self.call_center.call(id)
        elif command == "answer":
            msg = self.call_center.answer(id)
        elif command == "reject":
            msg = self.call_center.reject(id)
        elif command == "hangup":
            msg = self.call_center.hangup(id)

        msg_json = json.dumps({"response": msg})

        self.transport.write(msg_json.encode())

    def send_data(self, msg: str):
        data_json = json.dumps({"response": msg})
        self.transport.write(data_json.encode())


class CallCenter:
    def __init__(self, server, operators=[Operator("A"), Operator("B")]):
        self.operators = operators
        self.queue_calls = []
        self.active_calls = dict()
        self.timeout = dict()
        self.server = server

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
                    self.timeout[call_id] = reactor.callLater(10, self.ignored, call_id)
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
                self.timeout[call_id] = reactor.callLater(10, self.ignored, call_id)
                return msg

        self.queue_calls.append(call_id)
        msg += "Call " + call_id + " waiting in queue\n"
        return msg

    def answer(self, operator_id):
        try:
            call_id, operator = self.get_call_id(operator_id)
            self.active_calls[call_id] = (ANSWERED, operator)
            operator.status = "busy"
            msg = "Call " + call_id + " answered by operator " + operator_id + "\n"
            self.timeout[call_id].cancel()
            del self.timeout[call_id]
            return msg
        except:
            pass

    def reject(self, operator_id):
        try:
            call_id, operator = self.get_call_id(operator_id)
            operator.status = "available"
            del self.active_calls[call_id]
            print(self.queue_calls)
            self.queue_calls.insert(0, call_id)
            msg = "Call " + call_id + " rejected by operator " + operator_id + "\n"
            self.timeout[call_id].cancel()
            del self.timeout[call_id]
            msg += self.verify_operators()
            return msg
        except:
            pass

    def ignored(self, call_id):
        _, operator = self.active_calls[call_id]
        print(operator.id)
        operator.status = "available"
        del self.active_calls[call_id]
        self.queue_calls.insert(0, call_id)
        self.timeout[call_id].cancel()
        del self.timeout[call_id]

        msg = "Call " + call_id + " ignored by operator " + operator.id + "\n"
        msg += self.verify_operators()

        self.server.send_data(msg)
        return

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

        elif call_id in self.timeout.keys():
            _, operator = self.active_calls[call_id]
            operator.status = "available"
            del self.active_calls[call_id]

            msg = "Call " + call_id + " ignored by operator " + operator.id + "\n"
            msg += self.verify_operators()
            del self.timeout[call_id]

            self.server.send_data(msg)
            return

        elif call_id in self.active_calls or call_id in self.queue_calls:
            msg = "Call " + call_id + " missed\n"
            if call_id in self.queue_calls:
                self.queue_calls.remove(call_id)

            if call_id in self.active_calls:
                _, operator = self.active_calls[call_id]
                operator.status = "available"
                del self.active_calls[call_id]
                msg += self.verify_operators()
            return msg

        return "Call " + call_id + " not found\n"


if __name__ == "__main__":
    endpoint = TCP4ServerEndpoint(reactor, 5678)
    endpoint.listen(ServerFactory())
    reactor.run()
