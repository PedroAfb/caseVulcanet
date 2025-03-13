import cmd

class Operator:
    def __init__(self, id):
        self.id = id
        self.status = "available"


class CallCenter(cmd.Cmd):
    def __init__(self, operators=[("A", Operator("A")), ("B", Operator("B"))]):
        super().__init__()
        self.operators = operators
        self.queue_calls = []
        self.active_calls = dict()


    def do_call(self, id):
        pass

    def do_answer(self, id):
        pass

    def do_reject(self, id):    
        pass

    def do_hangup(self, id):
        pass

if __name__ == '__main__':
    CallCenter().cmdloop()