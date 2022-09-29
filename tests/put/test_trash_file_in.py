import unittest

from mock import Mock, call, ANY

from trashcli.fstab import create_fake_volume_of
from trashcli.put.rules import AllIsOkRules
from trashcli.put.trash_directories_finder import TrashDirectoriesFinder
from trashcli.put.file_trasher import FileTrasher, TrashFileIn, AbsolutePaths
from trashcli.put.trash_result import TrashResult
from datetime import datetime
import os


class TestTrashFileIn(unittest.TestCase):
    def setUp(self):
        self.reporter = Mock()
        mount_points = ['/', 'sandbox/other_partition']
        self.fs = Mock()
        volumes = create_fake_volume_of(mount_points)
        self.logger = Mock()
        realpath = lambda x: x
        parent_path = os.path.dirname
        self.trash_file_in = TrashFileIn(self.fs,
                                         realpath,
                                         volumes,
                                         datetime.now,
                                         parent_path,
                                         self.logger,
                                         self.reporter)

    def test(self):
        path_maker = AbsolutePaths()
        # self.trash_file_in.trash_file_in('path', 'trash_dir_path', 'volume',
        #                                  path_maker, AllIsOkRules(), )
