import unittest

import six

from mock import Mock, call

from trashcli.rm import Filter
from six import StringIO


class TestTrashRmCmdRun(unittest.TestCase):
    def test_without_arguments(self):
        from trashcli.rm import RmCmd
        cmd = RmCmd(None, None, None, None, None)
        cmd.stderr = StringIO()
        cmd.run([None])

        assert ('Usage:\n    trash-rm PATTERN\n\nPlease specify PATTERN\n' ==
                cmd.stderr.getvalue())

    def test_without_pattern_argument(self):
        from trashcli.rm import RmCmd
        cmd = RmCmd(None, None, None, None, None)
        cmd.stderr = StringIO()
        cmd.file_reader = Mock([])
        cmd.file_reader.exists = Mock([], return_value=None)
        cmd.file_reader.entries_if_dir_exists = Mock([], return_value=[])
        cmd.environ = {}
        cmd.getuid = lambda: '111'
        cmd.list_volumes = lambda: ['/vol1']

        cmd.run([None, None])

        assert '' == cmd.stderr.getvalue()


class TestTrashRmCmd(unittest.TestCase):

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
