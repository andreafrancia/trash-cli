import os
import unittest
from datetime import datetime

from mock import Mock

from trashcli.fstab import create_fake_volume_of
from trashcli.put.file_trasher import TrashFileIn
from trashcli.put.path_maker import PathMaker


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
        path_maker = PathMaker()
        # self.trash_file_in.trash_file_in('path', 'trash_dir_path', 'volume',
        #                                  path_maker, AllIsOkRules(), )
