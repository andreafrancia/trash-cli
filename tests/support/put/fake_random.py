from typing import List

from trashcli.put.core.int_generator import IntGenerator


class FakeRandomInt(IntGenerator):
    def __init__(self,
                 values,  # type: List[int]
                 ):
        self.values = values

    def new_int(self, _a, _b):
        return self.values.pop(0)

    def set_reply(self, value):
        self.values = [value]
