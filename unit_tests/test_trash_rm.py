from nose.tools import istest, assert_items_equal
from mock import Mock, call

class TestTrashRmCmd:
    @istest
    def a_star_matches_all(self):
        self.trash_contents.list_files_to = lambda out:(
            out.garbage('/foo', 'info/foo', 'files/foo'),
            out.garbage('/bar', 'info/bar', 'files/bar')
            )

        self.cmd.clean_up_matching('*')

        assert_items_equal([
            call.release('info/foo'),
            call.release('info/bar'),
            ], self.trashcan.mock_calls)

    @istest
    def basename_matches(self):
        self.trash_contents.list_files_to = lambda out:(
            out.garbage('/foo', 'info/foo', 'files/foo'),
            out.garbage('/bar', 'info/bar', 'files/bar')
            )

        self.cmd.clean_up_matching('foo')

        assert_items_equal([
            call.release('info/foo'),
            ], self.trashcan.mock_calls)

    @istest
    def example_with_star_dot_o(self):
        self.trash_contents.list_files_to = lambda out:(
            out.garbage('/foo.h', 'info/foo.h', 'files/foo.h'),
            out.garbage('/foo.c', 'info/foo.c', 'files/foo.c'),
            out.garbage('/foo.o', 'info/foo.o', 'files/foo.o'),
            out.garbage('/bar.o', 'info/bar.o', 'files/bar.o')
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

import os
class TrashRmCmd:

    def __init__(self, trash_contents, trashcan):
        self.trash_contents = trash_contents
        self.delete = TrashCanCleaner(trashcan)

    def clean_up_matching(self, pattern):
        self.filter = Pattern(pattern, self.delete)
        self.trash_contents.list_files_to(self.filter)

import fnmatch
class Pattern:
    def __init__(self, pattern, delete):
        self.delete = delete
        self.pattern = pattern
    def garbage(self, original_path, info, file):
        basename = os.path.basename(original_path)
        if fnmatch.fnmatchcase(basename, self.pattern):
            self.delete.garbage(original_path, info, file)

class TrashCanCleaner:
    def __init__(self, trashcan):
        self.trashcan = trashcan
    def garbage(self, original_path, info_file, backup_copy):
        self.trashcan.release(info_file)
