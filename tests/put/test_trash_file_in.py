import unittest

import flexmock
from mock import Mock
from mock.mock import call
from typing import cast

from trashcli.put.security_check import all_is_ok_rules
from trashcli.put.trash_file_in import TrashFileIn
from trashcli.put.trash_dir_volume import TrashDirVolume
from trashcli.put.info_dir import InfoDir
from trashcli.put.suffix import Suffix
from trashcli.put.trash_directory_for_put import TrashDirectoryForPut


class TestTrashFileIn(unittest.TestCase):
    def setUp(self):
        self.reporter = Mock()
        self.fs = Mock()
        self.logger = Mock()
        self.suffix = Mock(spec=Suffix)
        self.suffix.suffix_for_index.return_value = '_suffix'
        info_dir = InfoDir(self.fs, self.logger, self.suffix)
        self.trash_dir = flexmock.Mock(spec=TrashDirectoryForPut)
        self.trash_dir_volume = flexmock.Mock(spec=TrashDirVolume)
        self.trash_file_in = TrashFileIn(
            self.fs,
            self.reporter,
            info_dir,
            cast(TrashDirectoryForPut, self.trash_dir),
            cast(TrashDirVolume, self.trash_dir_volume)
        )

    def test_same_disk(self):
        flexmock.flexmock(self.trash_dir).should_receive('trash2'). \
            with_args('path', 'program_name', 99, 'path-maker-type',
                      'volume', "/disk1/trash_dir_path").and_return(True)
        flexmock.flexmock(self.trash_dir_volume). \
            should_receive('volume_of_trash_dir'). \
            with_args("/disk1/trash_dir_path").and_return('/disk1')

        result = self.trash_file_in.trash_file_in('path',
                                                  '/disk1/trash_dir_path',
                                                  'volume',
                                                  "path-maker-type",
                                                  all_is_ok_rules, True,
                                                  '/disk1', 'program_name', 99,
                                                  {})

        assert result == True
        assert self.reporter.mock_calls == [
            call.log_info_messages([], 'program_name', 99),
            call.trash_dir_with_volume('/disk1/trash_dir_path', '/disk1',
                                       'program_name', 99),
            call.file_has_been_trashed_in_as('path', '/disk1/trash_dir_path',
                                             'program_name', 99, {})]

    def test_different_disk(self):
        flexmock.flexmock(self.trash_dir_volume). \
            should_receive('volume_of_trash_dir'). \
            with_args("/disk1/trash_dir_path").and_return('/disk1')

        result = self.trash_file_in.trash_file_in('path',
                                                  '/disk1/trash_dir_path',
                                                  'volume',
                                                  "path_maker-type",
                                                  all_is_ok_rules, True,
                                                  '/disk2', 'program_name', 99,
                                                  {})

        assert result == True
        assert self.reporter.mock_calls == [
            call.log_info_messages([], 'program_name', 99),
            call.trash_dir_with_volume('/disk1/trash_dir_path', '/disk1',
                                       'program_name', 99),
            call.wont_use_trash_dir_because_in_a_different_volume('path',
                                                                  '/disk1/trash_dir_path',
                                                                  '/disk2',
                                                                  '/disk1',
                                                                  'program_name',
                                                                  99, {})]

    def test_error_while_trashing(self):
        flexmock.flexmock(self.trash_dir_volume). \
            should_receive('volume_of_trash_dir'). \
            with_args("/disk1/trash_dir_path").and_return('/disk1')
        io_error = IOError('error')
        flexmock.flexmock(self.trash_dir).should_receive('trash2'). \
            and_raise(io_error)

        result = self.trash_file_in.trash_file_in('path',
                                                  '/disk1/trash_dir_path',
                                                  'volume',
                                                  "path-maker-type",
                                                  all_is_ok_rules,
                                                  False,
                                                  '/disk1',
                                                  'program_name',
                                                  99,
                                                  {})
        assert result == False
        assert self.reporter.mock_calls == [
            call.log_info_messages([], 'program_name', 99),
            call.trash_dir_with_volume('/disk1/trash_dir_path', '/disk1',
                                       'program_name', 99),
            call.unable_to_trash_file_in_because('path',
                                                 '/disk1/trash_dir_path',
                                                 io_error,
                                                 'program_name', 99, {})]
