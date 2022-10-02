import os
import unittest
from datetime import datetime

from mock import Mock

from trashcli.fstab import create_fake_volume_of
from trashcli.put.file_trasher import TrashFileIn
from trashcli.put.info_dir import InfoDir
from trashcli.put.original_location import OriginalLocation, parent_realpath
from trashcli.put.path_maker import PathMaker
from trashcli.put.suffix import Suffix
from trashcli.put.trash_directory_for_put import TrashDirectoryForPut
from trashcli.put.clock import RealClock


class TestTrashFileIn(unittest.TestCase):
    def setUp(self):
        self.reporter = Mock()
        mount_points = ['/', 'sandbox/other_partition']
        self.fs = Mock()
        volumes = create_fake_volume_of(mount_points)
        self.logger = Mock()
        realpath = lambda x: x
        parent_path = os.path.dirname
        self.suffix = Mock(spec=Suffix)
        self.suffix.suffix_for_index.return_value = '_suffix'
        info_dir = InfoDir(self.fs, self.logger, self.suffix)
        path_maker = PathMaker()
        original_location = OriginalLocation(parent_realpath, path_maker)
        self.trash_dir = TrashDirectoryForPut(self.fs,
                                              info_dir,
                                              original_location,
                                              RealClock())
        self.trash_file_in = TrashFileIn(self.fs,
                                         realpath,
                                         volumes,
                                         datetime.now,
                                         parent_path,
                                         self.reporter,
                                         info_dir,
                                         self.trash_dir)

    def test(self):
        path_maker = PathMaker()
        # self.trash_file_in.trash_file_in('path', 'trash_dir_path', 'volume',
        #                                  path_maker, AllIsOkRules(), )
