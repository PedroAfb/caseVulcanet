import cmd


class CommandInterpreter(cmd.Cmd):
    def __init__(self, client):
        super().__init__()
        self.client = client

    def do_call(self, call_id: int):
        if not call_id:
            print("Call ID is required")
            return

        elif not call_id.isdigit():
            print("Call ID must be a number")
            return

        self.client.send_data(["call", call_id])

    def do_answer(self, operator_id: str):
        if not operator_id:
            print("Operator ID is required")
            return

        elif operator_id.isdigit():
            print("Operator ID must be a letter (A-Z)")
            return

        self.client.send_data(["answer", operator_id])

    def do_reject(self, operator_id: str):
        if not operator_id:
            print("Operator ID is required")
            return

        elif operator_id.isdigit():
            print("Operator ID must be a letter (A-Z)")
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
        self.client.close_connection()
        return True
