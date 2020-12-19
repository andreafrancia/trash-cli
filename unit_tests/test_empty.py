import unittest

from trashcli.empty import EmptyCmd
from mock import Mock, call
from unit_tests.tools import assert_equal


class TestTrashEmptyCmd(unittest.TestCase):
    def setUp(self):
        self.empty_all_trashdirs = Mock()
        self.empty_trashdir = Mock()

        self.cmd = EmptyCmd(None, None, None, None, None, None, None, None, None)
        self.cmd.empty_all_trashdirs = self.empty_all_trashdirs
        self.cmd.empty_trashdir = self.empty_trashdir

    def test_default_behaviour_is_emtpy_all_trashdirs(self):
        self.cmd.run('trash-empty')

        assert_equal([call()], self.empty_all_trashdirs.mock_calls)
        assert_equal([], self.empty_trashdir.mock_calls)

    def test(self):
        self.cmd.run('trash-empty', '--trash-dir', 'specific')

        assert_equal([], self.empty_all_trashdirs.mock_calls)
        assert_equal([call('specific')], self.empty_trashdir.mock_calls)
