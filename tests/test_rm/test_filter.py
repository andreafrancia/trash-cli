import unittest

from trashcli.rm.filter import Filter


class TestFilter(unittest.TestCase):

    def test_a_star_matches_all(self):
        self.cmd = Filter('*')

        assert self.cmd.matches('foo') == True
        assert self.cmd.matches('bar') == True

    def test_basename_matches(self):
        self.cmd = Filter('foo')

        assert self.cmd.matches('foo') == True
        assert self.cmd.matches('bar') == False

    def test_example_with_star_dot_o(self):
        self.cmd = Filter('*.o')

        assert self.cmd.matches('/foo.h') == False
        assert self.cmd.matches('/foo.c') == False
        assert self.cmd.matches('/foo.o') == True
        assert self.cmd.matches('/bar.o') == True

    def test_absolute_pattern(self):
        self.cmd = Filter('/foo/bar.baz')

        assert self.cmd.matches('/foo/bar.baz') == True
        assert self.cmd.matches('/foo/bar') == False

    def test(self):
        self.cmd = Filter('/foo/*.baz')

        assert self.cmd.matches('/foo/bar.baz') == True
        assert self.cmd.matches('/foo/bar.bar') == False
