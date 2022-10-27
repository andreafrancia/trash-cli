import unittest

import flexmock
from mock import Mock
from mock.mock import call
from typing import cast

from trashcli.put.candidate import Candidate
from trashcli.put.dir_maker import DirMaker
from trashcli.put.my_logger import LogData
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
        self.dir_maker = cast(DirMaker, flexmock.Mock(spec=DirMaker))
        info_dir = InfoDir(self.fs, self.logger, self.suffix)
        self.trash_dir = flexmock.Mock(spec=TrashDirectoryForPut)
        self.trash_dir_volume = flexmock.Mock(spec=TrashDirVolume)
        self.trash_file_in = TrashFileIn(
            self.fs,
            self.reporter,
            info_dir,
            cast(TrashDirectoryForPut, self.trash_dir),
            cast(TrashDirVolume, self.trash_dir_volume),
            self.dir_maker,
        )

    def test_same_disk(self):
        flexmock.flexmock(self.trash_dir).should_receive('trash2'). \
            with_args('path', 'log_data', 'path-maker-type',
                      'volume', "/disk1/trash_dir_path/info").and_return(True)
        flexmock.flexmock(self.trash_dir_volume). \
            should_receive('volume_of_trash_dir'). \
            with_args("/disk1/trash_dir_path").and_return('/disk1')
        flexmock.flexmock(self.dir_maker).should_receive('mkdir_p'). \
            with_args("/disk1/trash_dir_path/files", 0o700)
        flexmock.flexmock(self.dir_maker).should_receive('mkdir_p'). \
            with_args("/disk1/trash_dir_path", 0o700)
        flexmock.flexmock(self.dir_maker).should_receive('mkdir_p'). \
            with_args("/disk1/trash_dir_path/info", 0o700)

        candidate = Candidate(trash_dir_path='/disk1/trash_dir_path',
                              volume='volume',
                              path_maker_type="path-maker-type",
                              check_type=all_is_ok_rules)
        result = self.trash_file_in.trash_file_in('path',
                                                  candidate,
                                                  True,
                                                  '/disk1',
                                                  cast(LogData, 'log_data'),
                                                  {})

        assert result == True
        assert self.reporter.mock_calls == [
            call.log_info_messages([], 'log_data'),
            call.trash_dir_with_volume('/disk1/trash_dir_path', '/disk1',
                                       'log_data'),
            call.file_has_been_trashed_in_as('path', '/disk1/trash_dir_path',
                                             'log_data', {})]

    def test_different_disk(self):
        flexmock.flexmock(self.trash_dir_volume). \
            should_receive('volume_of_trash_dir'). \
            with_args("/disk1/trash_dir_path").and_return('/disk1')

        candidate = Candidate(trash_dir_path='/disk1/trash_dir_path',
                              volume='volume',
                              path_maker_type="path_maker-type",
                              check_type=all_is_ok_rules)
        result = self.trash_file_in.trash_file_in('path',
                                                  candidate,
                                                  True,
                                                  '/disk2',
                                                  cast(LogData, 'log_data'),
                                                  {})

        assert result == True
        assert self.reporter.mock_calls == [
            call.log_info_messages([], 'log_data'),
            call.trash_dir_with_volume('/disk1/trash_dir_path', '/disk1',
                                       'log_data'),
            call.wont_use_trash_dir_because_in_a_different_volume('path',
                                                                  '/disk1/trash_dir_path',
                                                                  '/disk2',
                                                                  '/disk1',
                                                                  'log_data',
                                                                  {})]

    def test_error_while_trashing(self):
        flexmock.flexmock(self.trash_dir_volume). \
            should_receive('volume_of_trash_dir'). \
            with_args("/disk1/trash_dir_path").and_return('/disk1')
        io_error = IOError('error')
        flexmock.flexmock(self.trash_dir).should_receive('trash2'). \
            and_raise(io_error)
        flexmock.flexmock(self.dir_maker).should_receive('mkdir_p'). \
            with_args("/disk1/trash_dir_path", 0o700)
        flexmock.flexmock(self.dir_maker).should_receive('mkdir_p'). \
            with_args("/disk1/trash_dir_path/files", 0o700)
        flexmock.flexmock(self.dir_maker).should_receive('mkdir_p'). \
            with_args("/disk1/trash_dir_path/info", 0o700)

        candidate = Candidate(trash_dir_path='/disk1/trash_dir_path',
                              volume='volume',
                              path_maker_type="path_maker-type",
                              check_type=all_is_ok_rules)
        result = self.trash_file_in.trash_file_in('path',
                                                  candidate,
                                                  False,
                                                  '/disk1',
                                                  cast(LogData, 'log_data'),
                                                  {})
        assert result == False
        assert self.reporter.mock_calls == [
            call.log_info_messages([], 'log_data'),
            call.trash_dir_with_volume('/disk1/trash_dir_path', '/disk1',
                                       'log_data'),
            call.unable_to_trash_file_in_because('path',
                                                 '/disk1/trash_dir_path',
                                                 io_error,
                                                 'log_data', {})]
