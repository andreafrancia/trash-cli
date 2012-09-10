from nose.tools import istest, assert_items_equal
from mock import Mock, call

from trashcli.rm import Filter

class TestTrashRmCmd:
    @istest
    def a_star_matches_all(self):

        self.cmd.use_pattern('*')
        self.cmd.delete_if_matches('/foo', 'info/foo')
        self.cmd.delete_if_matches('/bar', 'info/bar')

        assert_items_equal([
            call('info/foo'),
            call('info/bar'),
            ], self.delete_trashinfo_and_backup_copy.mock_calls)

    @istest
    def basename_matches(self):

        self.cmd.use_pattern('foo')
        self.cmd.delete_if_matches('/foo', 'info/foo'),
        self.cmd.delete_if_matches('/bar', 'info/bar')

        assert_items_equal([
            call('info/foo'),
            ], self.delete_trashinfo_and_backup_copy.mock_calls)

    @istest
    def example_with_star_dot_o(self):

        self.cmd.use_pattern('*.o')
        self.cmd.delete_if_matches('/foo.h', 'info/foo.h'),
        self.cmd.delete_if_matches('/foo.c', 'info/foo.c'),
        self.cmd.delete_if_matches('/foo.o', 'info/foo.o'),
        self.cmd.delete_if_matches('/bar.o', 'info/bar.o')

        assert_items_equal([
            call('info/foo.o'),
            call('info/bar.o'),
            ], self.delete_trashinfo_and_backup_copy.mock_calls)

    def setUp(self):
        self.delete_trashinfo_and_backup_copy = Mock()
        self.cmd = Filter(self.delete_trashinfo_and_backup_copy)

