import cmd
from call_center import CallCenter

class CommandInterpreter(cmd.Cmd):
    def __init__(self):
        self.call_center = CallCenter()

    def do_call(self, call_id):
        self.call_center.call(call_id)

    def do_answer(self, operator_id):
        self.call_center.answer(operator_id)

    def do_reject(self, operator_id):
        self.call_center.reject(operator_id)

    def do_hangup(self, call_id):
        self.call_center.hangup(call_id)

if __name__ == '__main__':
    CommandInterpreter.cmdloop()