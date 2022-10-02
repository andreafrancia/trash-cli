import os
import unittest
from datetime import datetime

import flexmock
from mock import Mock
from trashcli.fstab import create_fake_volume_of
from trashcli.put.security_check import all_is_ok_rules
from trashcli.put.trash_file_in import TrashFileIn
from trashcli.put.info_dir import InfoDir
from trashcli.put.suffix import Suffix
from trashcli.put.trash_directory_for_put import TrashDirectoryForPut


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
        self.trash_dir = flexmock.Mock(spec=TrashDirectoryForPut)
        self.trash_file_in = TrashFileIn(self.fs,
                                         realpath,
                                         volumes,
                                         datetime.now,
                                         parent_path,
                                         self.reporter,
                                         info_dir,
                                         self.trash_dir)

    def test(self):
        result = self.trash_file_in.trash_file_in('path', 'trash_dir_path',
                                                  'volume',
                                                  "path_maker-type",
                                                  all_is_ok_rules, True,
                                                  '/disk', 'program_name', 99,
                                                  {})
        assert result == True
