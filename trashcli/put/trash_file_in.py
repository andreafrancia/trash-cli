from typing import Dict

from trashcli.put.candidate import Candidate
from trashcli.put.dir_maker import DirMaker
from trashcli.put.fs import Fs
from trashcli.put.my_logger import LogData
from trashcli.put.reporter import TrashPutReporter
from trashcli.put.security_check import SecurityCheck
from trashcli.put.trash_directory_for_put import TrashDirectoryForPut
from trashcli.put.trashee import Trashee
from trashcli.put.trashing_checker import TrashingChecker


class TrashFileIn:
    def __init__(self,
                 fs,  # type: Fs
                 reporter,  # type: TrashPutReporter
                 trash_dir,  # type: TrashDirectoryForPut
                 trashing_checker,  # type: TrashingChecker
                 dir_maker,  # type: DirMaker
                 ):
        self.reporter = reporter
        self.security_check = SecurityCheck(fs)
        self.trash_dir = trash_dir
        self.dir_maker = dir_maker
        self.trashing_checker = trashing_checker

    def trash_file_in(self,
                      candidate,  # type: Candidate
                      log_data,  # type: LogData
                      environ,  # type: Dict[str, str]
                      trashee,  # type: Trashee
                      ):  # type: (...) -> bool
        file_has_been_trashed = False
        trash_dir_is_secure, messages = self.security_check. \
            check_trash_dir_is_secure(candidate)
        self.reporter.log_info_messages(messages, log_data)

        if not trash_dir_is_secure:
            self.reporter.trash_dir_is_not_secure(candidate.norm_path(),
                                                  log_data)
            return False
        self.reporter.trash_dir_with_volume(candidate, log_data)

        could_be_trashed_in = self.trashing_checker.file_could_be_trashed_in(
            trashee, candidate)
        if not could_be_trashed_in:
            self.reporter.wont_use_trash_dir_because_in_a_different_volume(
                trashee, log_data, environ, candidate)
            return False

        error = self.try_trash(candidate, log_data, environ, trashee)
        if error:
            self.reporter.unable_to_trash_file_in_because(
                trashee.path, candidate.norm_path(), error, log_data,
                environ)
            return False

        return True

    def try_trash(self,
                  candidate,  # type: Candidate
                  log_data,  # type : LogData
                  environ,  # type: Dict[str, str]
                  trashee,  # type: Trashee
                  ):
        try:
            self.dir_maker.mkdir_p(candidate.trash_dir_path, 0o700)
            self.dir_maker.mkdir_p(candidate.files_dir(), 0o700)
            self.dir_maker.mkdir_p(candidate.info_dir(), 0o700)

            self.trash_dir.trash2(trashee.path, candidate, log_data)
            self.reporter.file_has_been_trashed_in_as(trashee.path,
                                                      candidate,
                                                      log_data,
                                                      environ)
            return None
        except (IOError, OSError) as error:
            return error
