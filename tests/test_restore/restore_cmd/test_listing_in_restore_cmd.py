import unittest

from mock import Mock

from trashcli.restore.file_system import FakeRestoreFileSystem
from trashcli.fs import contents_of
from trashcli.restore import RestoreCmd, TrashedFiles, make_trash_directories


class TestListingInRestoreCmd(unittest.TestCase):
    def setUp(self):
        trash_directories = make_trash_directories()
        self.logger = Mock(spec=[])
        trashed_files = TrashedFiles(self.logger,
                                     trash_directories,
                                     None,
                                     contents_of)
        self.cmd = RestoreCmd(None, None,
                              exit=None,
                              input=None,
                              trashed_files=trashed_files,
                              mount_points=lambda: [],
                              fs=FakeRestoreFileSystem("dir"))
        self.cmd.handle_trashed_files = self.capture_trashed_files
        self.trashed_files = Mock(spec=['all_trashed_files'])
        self.cmd.trashed_files = self.trashed_files

    def test_with_no_args_and_files_in_trashcan(self):
        self.trashed_files.all_trashed_files.return_value = [
            FakeTrashedFile('<date>', 'dir/location'),
            FakeTrashedFile('<date>', 'dir/location'),
            FakeTrashedFile('<date>', 'anotherdir/location')
        ]

        self.cmd.run(['trash-restore'])

        assert [
                   'dir/location'
                   , 'dir/location'
               ] == self.original_locations

    def test_with_no_args_and_files_in_trashcan_2(self):
        self.trashed_files.all_trashed_files.return_value = [
            FakeTrashedFile('<date>', '/dir/location'),
            FakeTrashedFile('<date>', '/dir/location'),
            FakeTrashedFile('<date>', '/specific/path'),
        ]

        self.cmd.run(['trash-restore', '/specific/path'])

        assert self.original_locations == ['/specific/path']

    def test_with_with_path_prefix_bug(self):
        self.trashed_files.all_trashed_files.return_value = [
            FakeTrashedFile('<date>', '/prefix'),
            FakeTrashedFile('<date>', '/prefix-with-other'),
        ]

        self.cmd.run(['trash-restore', '/prefix'])

        assert self.original_locations == ['/prefix']

    def capture_trashed_files(self, arg, overwrite=False):
        self.original_locations = []
        for trashed_file in arg:
            self.original_locations.append(trashed_file.original_location)


class FakeTrashedFile(object):
    def __init__(self, deletion_date, original_location):
        self.deletion_date = deletion_date
        self.original_location = original_location

    def __repr__(self):
        return ('FakeTrashedFile(\'%s\', \'%s\')' % (self.deletion_date,
                                                     self.original_location))
