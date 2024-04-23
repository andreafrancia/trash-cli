from trashcli.put.core.int_generator import IntGenerator
from trashcli.put.suffix import Suffix


class TestSuffix:
    def setup_method(self):
        self.suffix = Suffix(InlineFakeIntGen(lambda x, y: "%s,%s" % (x, y)))

    def test_first_attempt(self):
        assert self.suffix.suffix_for_index(0) == ''

    def test_second_attempt(self):
        assert self.suffix.suffix_for_index(1) == '_1'

    def test_hundredth_attempt(self):
        assert self.suffix.suffix_for_index(100) == '_0,65535'


class InlineFakeIntGen(IntGenerator):
    def __init__(self, func):
        self.func = func

    def new_int(self, a, b):
        return self.func(a, b)
