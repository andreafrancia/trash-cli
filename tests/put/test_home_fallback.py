import os
import unittest
from datetime import datetime

import flexmock
from mock import Mock
from typing import cast

from trashcli.fstab import create_fake_volume_of
from trashcli.put.file_trasher import FileTrasher
from trashcli.put.trash_file_in import TrashFileIn
from trashcli.put.suffix import Suffix
from trashcli.put.trash_directories_finder import TrashDirectoriesFinder
from trashcli.put.trash_directory_for_put import TrashDirectoryForPut
from trashcli.put.trash_result import TrashResult


class TestHomeFallback(unittest.TestCase):
    def setUp(self):
        self.reporter = Mock()
        mount_points = ['/', 'sandbox/other_partition']
        self.fs = Mock()
        volumes = create_fake_volume_of(mount_points)
        trash_directories_finder = TrashDirectoriesFinder(volumes)
        self.logger = Mock()
        parent_path = os.path.dirname
        self.suffix = Mock(spec=Suffix)
        self.suffix.suffix_for_index.return_value = '_suffix'
        self.trash_dir = flexmock.Mock(spec=TrashDirectoryForPut)
        self.trash_file_in = flexmock.Mock(spec=TrashFileIn)
        self.file_trasher = FileTrasher(volumes,
                                        datetime.now,
                                        trash_directories_finder,
                                        parent_path,
                                        self.logger,
                                        self.reporter,
                                        cast(TrashFileIn, self.trash_file_in))

    def test_use_of_top_trash_dir_when_sticky(self):
        self.trash_file_in.should_receive(
            'trash_file_in').with_args(
            "sandbox/foo", ".Trash/123", "", "relative_paths",
            "top_trash_dir_rules", False, "", "trash-put", 99, {},
        ).and_return(True)
        result = self.file_trasher.trash_file('sandbox/foo',
                                              None,
                                              None,
                                              TrashResult(False),
                                              {},
                                              123,
                                              'trash-put',
                                              99)
        assert result == TrashResult(False)
