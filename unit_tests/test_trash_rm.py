from nose.tools import istest, assert_equals
from unit_tests.tools import assert_items_equal
from mock import Mock, call

from trashcli.rm import Filter
from unit_tests.myStringIO import StringIO

class TestTrashRmCmdRun:
    def test_without_arguments(self):
        from trashcli.rm import RmCmd
        cmd = RmCmd(None, None, None, None, None)
        cmd.stderr = StringIO()
        cmd.run([None])

        assert_equals('Usage:\n    trash-rm PATTERN\n\nPlease specify PATTERN\n', cmd.stderr.getvalue())

    def test_without_pattern_argument(self):
        from trashcli.rm import RmCmd
        cmd = RmCmd(None, None, None, None, None)
        cmd.stderr = StringIO()
        cmd.file_reader = Mock([])
        cmd.file_reader.exists = Mock([], return_value = None)
        cmd.file_reader.entries_if_dir_exists = Mock([], return_value = [])
        cmd.environ = {}
        cmd.getuid = lambda : '111'
        cmd.list_volumes = lambda: ['/vol1']

        cmd.run([None, None])

        assert_equals('', cmd.stderr.getvalue())

class TestTrashRmCmd:
    def test_a_star_matches_all(self):

        self.cmd.use_pattern('*')
        self.cmd.delete_if_matches('/foo', 'info/foo')
        self.cmd.delete_if_matches('/bar', 'info/bar')

        assert_items_equal([
            call('info/foo'),
            call('info/bar'),
            ], self.delete_trashinfo_and_backup_copy.mock_calls)

    def test_basename_matches(self):

        self.cmd.use_pattern('foo')
        self.cmd.delete_if_matches('/foo', 'info/foo'),
        self.cmd.delete_if_matches('/bar', 'info/bar')

        assert_items_equal([
            call('info/foo'),
            ], self.delete_trashinfo_and_backup_copy.mock_calls)

    def test_example_with_star_dot_o(self):

        self.cmd.use_pattern('*.o')
        self.cmd.delete_if_matches('/foo.h', 'info/foo.h'),
        self.cmd.delete_if_matches('/foo.c', 'info/foo.c'),
        self.cmd.delete_if_matches('/foo.o', 'info/foo.o'),
        self.cmd.delete_if_matches('/bar.o', 'info/bar.o')

        assert_items_equal([
            call('info/foo.o'),
            call('info/bar.o'),
            ], self.delete_trashinfo_and_backup_copy.mock_calls)

    def test_absolute_pattern(self):
        self.cmd.use_pattern('/foo/bar.baz')
        self.cmd.delete_if_matches('/foo/bar.baz', '1'),
        self.cmd.delete_if_matches('/foo/bar', '2'),

        assert_items_equal([
            call('1'),
            ], self.delete_trashinfo_and_backup_copy.mock_calls)


    def setUp(self):
        self.delete_trashinfo_and_backup_copy = Mock()
        self.cmd = Filter(self.delete_trashinfo_and_backup_copy)

