import cmd
from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ClientFactory as CLFactory
from twisted.internet.endpoints import TCP4ClientEndpoint
import json


class ClientFactory(CLFactory):
    def buildProtocol(self, addr):
        return Client()


class Client(Protocol):
    def connectionMade(self):
        print("Connection made (client saying)")
        reactor.callInThread(CommandInterpreter(self).cmdloop)

    def dataReceived(self, data):
        data_list = data.decode().split("}")
        if len(data_list) > 1:
            for i in range(len(data_list) - 1):
                json_obj = data_list[i] + "}"
                data_json = json.loads(json_obj)
                print(data_json["response"])
        else:
            data_json = json.loads(data.decode())
            print(data_json["response"])

    def send_data(self, data: list):
        data_json = json.dumps({"command": data[0], "id": data[1]})
        self.transport.write(data_json.encode())


class CommandInterpreter(cmd.Cmd):
    def __init__(self, client):
        super().__init__()
        self.client = client

    def do_call(self, call_id: int):
        if not call_id:
            print("Call ID is required")
            return
        if not call_id.isdigit():
            print("Call ID must be a number")
            return
        self.client.send_data(["call", call_id])

    def do_answer(self, operator_id: str):
        if not operator_id:
            print("Operator ID is required")
            return

        self.client.send_data(["answer", operator_id])

    def do_reject(self, operator_id: str):
        if not operator_id:
            print("Operator ID is required")
            return

        self.client.send_data(["reject", operator_id])

    def do_hangup(self, call_id: int):
        if not call_id:
            print("Call ID is required")
            return
        if not call_id.isdigit():
            print("Call ID must be a number")
            return
        self.client.send_data(["hangup", call_id])

    def do_exit(self, _):
        reactor.stop()
        return True


if __name__ == "__main__":
    factory = ClientFactory()
    endpoint = TCP4ClientEndpoint(reactor, "localhost", 5678)
    endpoint.connect(factory)
    reactor.run()
