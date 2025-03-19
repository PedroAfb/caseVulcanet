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
    def __init__(self):
        self.server = Server()
        self.call_center = CallCenter(self.server)
        self.server.set_call_center(self.call_center)

    def buildProtocol(self, addr):
        return self.server


class Server(Protocol):
    def __init__(self):
        self.call_center = None

    def set_call_center(self, call_center):
        self.call_center = call_center

    def connectionMade(self):
        print("Connection made (server saying)")

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

    def connectionLost(self, reason=...):
        print("Connection lost")
        reactor.stop()


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
        return None, None

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
        if call_id in self.active_calls or call_id in self.queue_calls:
            return "Call " + call_id + " already in progress\n"
        else:
            msg = "Call " + call_id + " received\n"

            for operator in self.operators:
                if operator.status == "available":
                    msg += (
                        "Call "
                        + call_id
                        + " ringing for operator "
                        + operator.id
                        + "\n"
                    )
                    operator.status = "ringing"
                    self.active_calls[call_id] = (NOT_ANSWERED, operator)
                    self.timeout[call_id] = reactor.callLater(10, self.ignored, call_id)
                    return msg

            self.queue_calls.append(call_id)
            msg += "Call " + call_id + " waiting in queue\n"
            return msg

    def answer(self, operator_id):
        call_id, operator = self.get_call_id(operator_id)
        if not call_id and not operator:
            return "No calls ringing for operator " + operator_id + "\n"

        self.active_calls[call_id] = (ANSWERED, operator)
        operator.status = "busy"
        msg = "Call " + call_id + " answered by operator " + operator_id + "\n"
        self.timeout[call_id].cancel()
        del self.timeout[call_id]
        return msg

    def reject(self, operator_id):
        call_id, operator = self.get_call_id(operator_id)
        if not call_id and not operator:
            return "No calls ringing for operator " + operator_id + "\n"

        elif self.active_calls[call_id][0] == ANSWERED:
            return (
                "Call "
                + call_id
                + " already answered by operator "
                + operator_id
                + "\n"
            )

        operator.status = "available"
        del self.active_calls[call_id]
        print(self.queue_calls)
        self.queue_calls.append(call_id)
        msg = "Call " + call_id + " rejected by operator " + operator_id + "\n"
        self.timeout[call_id].cancel()
        del self.timeout[call_id]
        msg += self.verify_operators()
        return msg

    def ignored(self, call_id):
        if call_id in self.active_calls:
            _, operator = self.active_calls[call_id]
            operator.status = "available"
            del self.active_calls[call_id]
            self.queue_calls.append(call_id)
            del self.timeout[call_id]

            msg = "Call " + call_id + " ignored by operator " + operator.id + "\n"
            msg += self.verify_operators()

            self.server.send_data(msg)

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
