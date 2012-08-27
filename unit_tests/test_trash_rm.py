from nose.tools import istest, assert_items_equal
from mock import Mock, call

from trashcli.rm import TrashRmCmd

class TestTrashRmCmd:
    @istest
    def a_star_matches_all(self):
        self.trash_contents.list_files_to = lambda out:(
            out.garbage('/foo', 'info/foo'),
            out.garbage('/bar', 'info/bar')
            )

        self.cmd.clean_up_matching('*')

        assert_items_equal([
            call.release('info/foo'),
            call.release('info/bar'),
            ], self.trashcan.mock_calls)

    @istest
    def basename_matches(self):
        self.trash_contents.list_files_to = lambda out:(
            out.garbage('/foo', 'info/foo'),
            out.garbage('/bar', 'info/bar')
            )

        self.cmd.clean_up_matching('foo')

        assert_items_equal([
            call.release('info/foo'),
            ], self.trashcan.mock_calls)

    @istest
    def example_with_star_dot_o(self):
        self.trash_contents.list_files_to = lambda out:(
            out.garbage('/foo.h', 'info/foo.h'),
            out.garbage('/foo.c', 'info/foo.c'),
            out.garbage('/foo.o', 'info/foo.o'),
            out.garbage('/bar.o', 'info/bar.o')
            )

        self.cmd.clean_up_matching('*.o')

        assert_items_equal([
            call.release('info/foo.o'),
            call.release('info/bar.o'),
            ], self.trashcan.mock_calls)

    def setUp(self):
        self.trash_contents = Mock()
        self.trashcan = Mock()
        self.cmd = TrashRmCmd(self.trash_contents, self.trashcan)

