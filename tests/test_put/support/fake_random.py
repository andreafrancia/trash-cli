from trashcli.put.core.int_generator import IntGenerator


class FakeRandomInt(IntGenerator):
    def __init__(self,
                 value,  # int
                 ):
        self.value = value

    def new_int(self, _a, _b):
        return self.value

    def set_reply(self, value):
        self.value = value
