import datetime
import unittest

from tests.put.support.dummy_clock import DummyClock

from flexmock import flexmock

from tests.support.capture_error import capture_error
from trashcli.put.info_dir import InfoDir
from trashcli.put.original_location import OriginalLocation
from trashcli.put.path_maker import PathMaker
from trashcli.put.real_fs import RealFs
from trashcli.put.trash_directory_for_put import TrashDirectoryForPut


class TestTrashDirectoryForPut(unittest.TestCase):
    def setUp(self):
        self.fs = flexmock(RealFs)
        self.path_maker = flexmock(PathMaker)
        self.info_dir = flexmock(InfoDir)
        self.original_location = flexmock(OriginalLocation)
        self.clock = DummyClock()
        self.trash_dir = TrashDirectoryForPut(self.fs,
                                              self.info_dir,
                                              self.original_location,
                                              self.clock)

    def test(self):
        self.mock_original_location('/disk/file-to-trash', 'path_maker_type',
                                    '/disk').and_return('original_location')
        self.mock_info_dir_persist_trash_info(
            'original_location',
            b"[Trash Info]\nPath=original_location\nDeletionDate=2014-01-01T00:00:00\n",
            "program_name", 99, "/info/dir").and_return('trash_info_path')
        self.mock_fs_move('/disk/file-to-trash', 'files/trash')
        self.clock.set_clock(datetime.datetime(2014, 1, 1, 0, 0, 0))

        self.trash_dir.trash2('/disk/file-to-trash',
                              "program_name",
                              99,
                              'path_maker_type',
                              '/disk',
                              '/info/dir')

    def test_when_io_erro(self):
        self.mock_original_location('/disk/file-to-trash', 'path_maker_type',
                                    '/disk').and_return('original_location')
        self.mock_info_dir_persist_trash_info(
            'original_location',
            b"[Trash Info]\nPath=original_location\nDeletionDate=2014-01-01T00:00:00\n",
            "program_name", 99, "/info/dir").and_return('trash_info_path')
        self.mock_fs_move('/disk/file-to-trash', 'files/trash').and_raise(
            IOError("No space left on device"))
        flexmock(self.fs).should_receive('remove_file').with_args(
            'trash_info_path')
        self.clock.set_clock(datetime.datetime(2014, 1, 1, 0, 0, 0))

        error = capture_error(lambda:
                              self.trash_dir.trash2('/disk/file-to-trash',
                                                    "program_name",
                                                    99,
                                                    'path_maker_type',
                                                    '/disk',
                                                    '/info/dir'))

        self.assertEqual("No space left on device", str(error))

    def mock_original_location(self, path, path_maker_type, volume_top_dir):
        return flexmock(self.original_location).should_receive('for_file'). \
            with_args(path, path_maker_type, volume_top_dir)

    def mock_info_dir_persist_trash_info(self, basename, content, program_name,
                                         verbose, info_dir_path):
        return flexmock(self.info_dir).should_receive('persist_trash_info'). \
            with_args(basename, content, program_name, verbose, info_dir_path)

    def mock_fs_move(self, path, dest):
        return flexmock(self.fs).should_receive('move').with_args(path, dest)
