from twisted.internet import reactor


class Operator:
    def __init__(self, id):
        self.id = id
        self.status = "available"


ANSWERED = True
NOT_ANSWERED = False


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

    def remove_operator_call_relation(self, call_id, operator=None):
        if not operator:
            _, operator = self.active_calls[call_id]

        if call_id in self.timeout:
            del self.timeout[call_id]

        operator.status = "available"
        del self.active_calls[call_id]
        msg = self.verify_operators()
        return msg

    def call(self, call_id):
        if call_id in self.active_calls or call_id in self.queue_calls:
            return "Call " + call_id + " is already active\n"

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

        msg = "Call " + call_id + " rejected by operator " + operator_id + "\n"
        self.queue_calls.append(call_id)
        self.timeout[call_id].cancel()
        msg += self.remove_operator_call_relation(call_id, operator)
        return msg

    def ignored(self, call_id):
        if call_id in self.active_calls:
            _, operator = self.active_calls[call_id]
            msg = "Call " + call_id + " ignored by operator " + operator.id + "\n"
            self.queue_calls.append(call_id)
            msg += self.remove_operator_call_relation(call_id, operator)

            self.server.send_data(msg)

    def hangup(self, call_id):
        msg = ""
        if call_id in self.active_calls and self.active_calls[call_id][0] == ANSWERED:
            _, operator = self.active_calls[call_id]
            msg = (
                "Call "
                + call_id
                + " finished and operator "
                + operator.id
                + " available\n"
            )
            msg += self.remove_operator_call_relation(call_id, operator)
            return msg

        elif call_id in self.active_calls or call_id in self.queue_calls:
            msg = "Call " + call_id + " missed\n"
            if call_id in self.queue_calls:
                self.queue_calls.remove(call_id)

            if call_id in self.active_calls:
                msg += self.remove_operator_call_relation(call_id)
            return msg

        return "Call " + call_id + " not found\n"
