import unittest

from mock import Mock
from six import StringIO

from trashcli.restore.file_system import FakeReadCwd
from trashcli.restore.handler import Handler
from trashcli.restore.restore_cmd import RestoreCmd
from trashcli.restore.trashed_file import TrashedFile
from trashcli.restore.trashed_files import TrashedFiles


class TestListingInRestoreCmd(unittest.TestCase):
    def setUp(self):
        self.logger = Mock(spec=[])
        self.trashed_files = Mock(spec=TrashedFiles)
        self.trashed_files.all_trashed_files = Mock()
        self.original_locations = []
        self.fake_handler = FakeHandler(self.original_locations)
        self.cmd = RestoreCmd(stdout=StringIO(),
                              version="0.0.0",
                              trashed_files=self.trashed_files,
                              read_cwd=FakeReadCwd("dir"),
                              handler=self.fake_handler)

    def test_with_no_args_and_files_in_trashcan(self):
        self.trashed_files.all_trashed_files.return_value = [
            a_trashed_file('dir/location'),
            a_trashed_file('dir/location'),
            a_trashed_file('anotherdir/location')
        ]

        self.cmd.run(['trash-restore'])

        assert [
                   'dir/location',
                   'dir/location'
               ] == self.original_locations

    def test_with_no_args_and_files_in_trashcan_2(self):
        self.trashed_files.all_trashed_files.return_value = [
            a_trashed_file('/dir/location'),
            a_trashed_file('/dir/location'),
            a_trashed_file('/specific/path'),
        ]

        self.cmd.run(['trash-restore', '/specific/path'])

        assert self.original_locations == ['/specific/path']

    def test_with_with_path_prefix_bug(self):
        self.trashed_files.all_trashed_files.return_value = [
            a_trashed_file('/prefix'),
            a_trashed_file('/prefix-with-other'),
        ]

        self.cmd.run(['trash-restore', '/prefix'])

        assert self.original_locations == ['/prefix']


def a_trashed_file(original_location):
    return TrashedFile(original_location=original_location,
                       deletion_date="a date",
                       info_file="",
                       original_file="")


class FakeHandler(Handler):
    def __init__(self, original_locations):
        self.original_locations = original_locations

    def handle_trashed_files(self, trashed_files, _overwrite):
        for trashed_file in trashed_files:
            self.original_locations.append(trashed_file.original_location)
