from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ServerFactory as SvFactory
from call_center import CallCenter
import json
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint


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
        data_dict = json.loads(data.decode())
        command = data_dict["command"]
        id = data_dict["id"]

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


if __name__ == "__main__":
    endpoint = TCP4ServerEndpoint(reactor, 5678)
    endpoint.listen(ServerFactory())
    reactor.run()
