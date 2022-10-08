import os
import unittest
from datetime import datetime

import flexmock
from mock import ANY, Mock, call
from typing import cast

from trashcli.fstab import create_fake_volume_of
from trashcli.put.file_trasher import FileTrasher
from trashcli.put.trash_file_in import TrashFileIn
from trashcli.put.info_dir import InfoDir
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
                                         cast(TrashDirectoryForPut,
                                              self.trash_dir))
        self.file_trasher = FileTrasher(self.fs,
                                        volumes,
                                        datetime.now,
                                        trash_directories_finder,
                                        parent_path,
                                        self.logger,
                                        self.reporter,
                                        self.trash_file_in)

    def test_use_of_top_trash_dir_when_sticky(self):
        flexmock.flexmock(self.trash_file_in).should_receive(
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

    def test_bug_will_use_top_trashdir_even_with_not_sticky(self):
        self.fs.mock_add_spec(['isdir', 'islink', 'has_sticky_bit',
                               'move', 'atomic_write',
                               'remove_file', 'ensure_dir'])
        self.fs.isdir.return_value = True
        self.fs.islink.return_value = False
        self.fs.has_sticky_bit.return_value = False
        flexmock.flexmock(self.trash_dir).should_receive('trash2')

        result = TrashResult(False)
        self.file_trasher.trash_file('sandbox/foo',
                                     None,
                                     None,
                                     result,
                                     {},
                                     123,
                                     'trash-put',
                                     99)

        assert self.fs.mock_calls == [
            call.isdir('.Trash'),
            call.islink('.Trash'),
            call.has_sticky_bit('.Trash'),
            call.ensure_dir('.Trash-123', 448),
            call.ensure_dir('.Trash-123/files', 448),
        ]
