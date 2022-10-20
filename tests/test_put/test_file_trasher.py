import unittest

import flexmock
from mock import Mock
from typing import cast

from tests.test_put.support.fake_fs_with_realpath import FakeFsWithRealpath
from trashcli.fstab import create_fake_volume_of, Volumes
from trashcli.put.file_trasher import FileTrasher
from trashcli.put.my_logger import MyLogger
from trashcli.put.parent_realpath import ParentRealpath
from trashcli.put.path_maker import PathMakerType
from trashcli.put.reporter import TrashPutReporter
from trashcli.put.security_check import top_trash_dir_rules
from trashcli.put.suffix import Suffix
from trashcli.put.trash_directories_finder import TrashDirectoriesFinder
from trashcli.put.trash_directory_for_put import TrashDirectoryForPut
from trashcli.put.trash_file_in import TrashFileIn
from trashcli.put.trash_result import TrashResult


class TestFileTrasher(unittest.TestCase):
    def setUp(self):
        self.reporter = flexmock.Mock(spec=TrashPutReporter)
        self.fs = FakeFsWithRealpath()
        self.volumes = flexmock.Mock(spec=Volumes)
        self.trash_directories_finder = flexmock.Mock(
            spec=TrashDirectoriesFinder)
        self.logger = flexmock.Mock(spec=MyLogger)
        self.parent_realpath = flexmock.Mock(spec=ParentRealpath)
        self.suffix = Mock(spec=Suffix)
        self.suffix.suffix_for_index.return_value = '_suffix'
        self.trash_dir = flexmock.Mock(spec=TrashDirectoryForPut)
        self.trash_file_in = flexmock.Mock(spec=TrashFileIn)
        self.file_trasher = FileTrasher(
            cast(Volumes, self.volumes),
            cast(TrashDirectoriesFinder, self.trash_directories_finder),
            cast(ParentRealpath, self.parent_realpath),
            cast(MyLogger, self.logger),
            cast(TrashPutReporter, self.reporter),
            cast(TrashFileIn, self.trash_file_in))
        self.parent_realpath.should_receive('parent_realpath').and_return('/')

    def set_trash_directory(self, trash_dir_path):
        self.trash_directories_finder.\
            should_receive('possible_trash_directories_for').\
            with_args("/", None, {}, 123).and_return([
            (trash_dir_path, "/", PathMakerType.relative_paths,
             top_trash_dir_rules)
        ])

    def test(self):
        self.reporter.should_receive('volume_of_file'). \
            with_args("/", "trash-put", 99)
        self.volumes.should_receive('volume_of').with_args("/"). \
            and_return('/')
        self.set_trash_directory('/trash-dir')
        self.trash_file_in.should_receive('trash_file_in').with_args(
            "sandbox/foo", "/trash-dir", "/", "relative_paths",
            top_trash_dir_rules, False, "/", "trash-put", 99, {},
        ).and_return(True)

        result = self.file_trasher.trash_file('sandbox/foo',
                                              None, # forced_volume
                                              None, # user_trash_dir
                                              TrashResult(False),
                                              {},
                                              123,
                                              'trash-put',
                                              99)
        assert result == TrashResult(False)

    def test_should_report_when_trash_fail(self):
        self.volumes.should_receive('volume_of').and_return('/')
        self.trash_file_in.should_receive('trash_file_in').and_return(False)
        result = TrashResult(False)
        self.set_trash_directory('/trash-dir')
        self.reporter.should_receive('volume_of_file')
        self.reporter.should_receive('unable_to_trash_file').\
            with_args("non-existent", "trash-put")

        self.file_trasher.trash_file('non-existent',
                                     None,
                                     None,
                                     result,
                                     {},
                                     123,
                                     'trash-put',
                                     99)

    def test_when_trash_file_in_fails(self):
        self.volumes.should_receive('volume_of').and_return('/')
        result = TrashResult(False)
        self.trash_file_in.should_receive('trash_file_in').and_return(False)
        self.set_trash_directory('/trash-dir')
        self.reporter.should_receive('volume_of_file')
        self.reporter.should_receive('unable_to_trash_file').\
            with_args("non-existent", "trash-put")

        self.file_trasher.trash_file("non-existent",
                                     None,
                                     None,
                                     result,
                                     {},
                                     123,
                                     'trash-put',
                                     99)
