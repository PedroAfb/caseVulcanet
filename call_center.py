
class Operator:
    def __init__(self, id):
        self.id = id
        self.status = "available"

ANSWERED = True
NOT_ANSWERED = False

class CallCenter():
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
                    print("Call", call_id, "ringing for operator", operator.id)
                    operator.status = "ringing"
                    self.active_calls[call_id] = (NOT_ANSWERED, operator)
                    return
    

    def call(self, call_id):
        print("Call", call_id, "received")

        for operator in self.operators:
            if operator.status == "available":
                print("Call", call_id, "ringing for operator ", operator.id)
                operator.status = "ringing"
                self.active_calls[call_id] = (NOT_ANSWERED, operator)
                return
            
        self.queue_calls.append(call_id)
        print("Call", call_id, "waiting in queue")


    def answer(self, operator_id):
        call_id, operator = self.get_call_id(operator_id)
        self.active_calls[call_id] = (ANSWERED, operator)
        print("Call", call_id, "answered by operator", operator_id)
        operator.status = "busy"


    def reject(self, operator_id):
        call_id, operator = self.get_call_id(operator_id)
        operator.status = "available"
        print("Call", call_id, "rejected by operator", operator.id)
        del self.active_calls[call_id]
        self.queue_calls.append(call_id)
        self.verify_operators()


    def hangup(self, call_id):
        if call_id in self.active_calls and self.active_calls[call_id][0] == ANSWERED:
            _, operator = self.active_calls[call_id]
            del self.active_calls[call_id]
            operator.status = "available"
            print("Call", call_id, "finished and operator", operator.id, "available")
            self.verify_operators()
        else:
            print("Call", call_id, "missed")
            if call_id in self.queue_calls:
                self.queue_calls.remove(call_id)

            if call_id in self.active_calls:
                _, operator = self.active_calls[call_id]
                operator.status = "available"
                del self.active_calls[call_id]
                self.verify_operators()
