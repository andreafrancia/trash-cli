from typing import List, Tuple

from trashcli.lib.environ import Environ
from trashcli.put.core.candidate import Candidate
from trashcli.put.core.failure_reason import FailureReason, LogContext, LogEntry
from trashcli.put.core.trashee import Trashee
from trashcli.put.fs.fs import Fs
from trashcli.put.janitor_tools.info_creator import TrashInfoCreator
from trashcli.put.janitor_tools.info_file_persister import InfoFilePersister
from trashcli.put.janitor_tools.put_trash_dir import PutTrashDir
from trashcli.put.janitor_tools.security_check import SecurityCheck
from trashcli.put.janitor_tools.trash_dir_checker import TrashDirChecker
from trashcli.put.janitor_tools.trash_dir_creator import TrashDirCreator
from trashcli.put.my_logger import LogData


class NoLog(FailureReason):
    def log_entries(self, context):  # type: (LogContext) -> List[LogEntry]
        return []


class Janitor:
    def __init__(self,
                 fs,  # type: Fs
                 trash_dir,  # type: PutTrashDir
                 trashing_checker,  # type: TrashDirChecker
                 info_dir,  # type: TrashInfoCreator
                 persister,  # type: InfoFilePersister
                 ):
        self.trash_dir = trash_dir
        self.trashing_checker = trashing_checker
        self.info_dir = info_dir
        self.security_check = SecurityCheck(fs)
        self.persister = persister
        self.dir_creator = TrashDirCreator(fs)

    def trash_file_in(self,
                      candidate,  # type: Candidate
                      log_data,  # type: LogData
                      environ,  # type: Environ
                      trashee,  # type: Trashee
                      ):  # type: (...) -> Tuple[bool, FailureReason]
        secure = self.security_check.check_trash_dir_is_secure(candidate)

        if secure.is_error():
            return False, secure.error()

        can_be_used = self.trashing_checker.file_could_be_trashed_in(
            trashee, candidate, environ)
        if can_be_used.is_error():
            return False, can_be_used.error()

        dirs_creation = self.dir_creator.make_candidate_dirs(candidate)
        if dirs_creation.is_error():
            return False, dirs_creation.error()

        trashinfo_data = self.info_dir.make_trashinfo_data(trashee.path,
                                                           candidate)
        if trashinfo_data.is_error():
            return False, trashinfo_data.error()

        trashed_file = self.persister.create_trashinfo_file(
            trashinfo_data.value(), log_data)

        trashed = self.trash_dir.try_trash(trashee.path, trashed_file)
        if trashed.is_error():
            return False, trashed.error()

        return True, NoLog()
