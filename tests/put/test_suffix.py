import unittest

from trashcli.put.suffix import Suffix


class TestSuffix(unittest.TestCase):
    def setUp(self):
        self.randint = lambda x, y: "%s,%s" % (x,y)
        self.suffix = Suffix(self.randint)

    def test_first_attempt(self):
        assert self.suffix.suffix_for_index(0) == ''

    def test_second_attempt(self):
        assert self.suffix.suffix_for_index(1) == '_1'

    def test_hundredth_attempt(self):
        assert self.suffix.suffix_for_index(100) == '_0,65535'
