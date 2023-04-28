import unittest

from mock import Mock

from trashcli.restore.file_system import FakeRestoreFileSystem
from trashcli.fs import contents_of
from trashcli.restore.handler import Handler
from trashcli.restore.restore_cmd import RestoreCmd
from trashcli.restore.trash_directories import make_trash_directories
from trashcli.restore.trashed_file import TrashedFiles


class TestListingInRestoreCmd(unittest.TestCase):
    def setUp(self):
        trash_directories = make_trash_directories()
        self.logger = Mock(spec=[])
        self.trashed_files = TrashedFiles(self.logger,
                                          trash_directories,
                                          None,
                                          contents_of)
        self.trashed_files.all_trashed_files = Mock()
        self.original_locations = []
        self.fake_handler = FakeHandler(self.original_locations)
        self.cmd = RestoreCmd(stdout=None,
                              version="0.0.0",
                              trashed_files=self.trashed_files,
                              mount_points=lambda: [],
                              fs=FakeRestoreFileSystem("dir"),
                              handler=self.fake_handler)

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


class FakeTrashedFile(object):
    def __init__(self, deletion_date, original_location):
        self.deletion_date = deletion_date
        self.original_location = original_location

    def __repr__(self):
        return ('FakeTrashedFile(\'%s\', \'%s\')' % (self.deletion_date,
                                                     self.original_location))


class FakeHandler(Handler):
    def __init__(self, original_locations):
        self.original_locations = original_locations

    def handle_trashed_files(self, trashed_files, _overwrite):
        for trashed_file in trashed_files:
            self.original_locations.append(trashed_file.original_location)
