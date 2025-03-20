from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ClientFactory as CLFactory
from command_interpreter import CommandInterpreter
import json
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint


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

    def close_connection(self):
        print("Closing connection")
        self.transport.loseConnection()
        reactor.callFromThread(reactor.stop)


if __name__ == "__main__":
    factory = ClientFactory()
    endpoint = TCP4ClientEndpoint(reactor, "localhost", 5678)
    endpoint.connect(factory)
    reactor.run()
