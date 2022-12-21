import os
import unittest

from mock import Mock
from trashcli import restore
from trashcli.fs import contents_of
from trashcli.restore import (
    RestoreCmd,
    TrashDirectory,
    TrashedFile,
    TrashedFiles,
    make_trash_directories,
)

from tests.support.files import make_empty_file
from tests.support.my_path import MyPath


class TestTrashedFileRestoreIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = MyPath.make_temp_dir()
        trash_directories = make_trash_directories()
        self.logger = Mock(spec=[])
        trashed_files = TrashedFiles(self.logger,
                                     trash_directories,
                                     TrashDirectory(),
                                     contents_of)
        self.cmd = RestoreCmd(None,
                              None,
                              exit=None,
                              input=None,
                              trashed_files=trashed_files,
                              mount_points=lambda: [],
                              fs=restore.FileSystem())

    def test_restore(self):
        trashed_file = Mock(sepc=TrashedFile)
        trashed_file.info_file = self.temp_dir / 'info_file'
        trashed_file.original_location = self.temp_dir / 'parent/path'
        trashed_file.deletion_date = None
        trashed_file.original_file = self.temp_dir / 'orig'

        make_empty_file(self.temp_dir / 'orig')
        make_empty_file(self.temp_dir / 'info_file')

        self.cmd.restore(trashed_file)

        assert os.path.exists(self.temp_dir / 'parent/path')
        assert not os.path.exists(self.temp_dir / 'info_file')
        assert not os.path.exists(self.temp_dir / 'orig')

    def test_restore_over_existing_file(self):
        trashed_file = Mock(sepc=TrashedFile)
        trashed_file.original_location = self.temp_dir / 'path'
        make_empty_file(self.temp_dir / 'path')

        self.assertRaises(IOError, lambda: self.cmd.restore(trashed_file))

    def tearDown(self):
        self.temp_dir.clean_up()
