from typing import List, NamedTuple

from trashcli.lib.environ import Environ
from trashcli.put.core.candidate import Candidate
from trashcli.put.core.either import Left
from trashcli.put.core.failure_reason import FailureReason, LogContext
from trashcli.put.core.logs import LogEntry
from trashcli.put.core.trashee import Trashee
from trashcli.put.fs.fs import Fs
from trashcli.put.janitor_tools.info_creator import TrashInfoCreator
from trashcli.put.janitor_tools.info_file_persister import InfoFilePersister
from trashcli.put.janitor_tools.put_trash_dir import PutTrashDir
from trashcli.put.janitor_tools.security_check import SecurityCheck
from trashcli.put.janitor_tools.trash_dir_checker import TrashDirChecker
from trashcli.put.janitor_tools.trash_dir_creator import TrashDirCreator
from trashcli.put.jobs import JobExecutor
from trashcli.put.my_logger import LogData
from trashcli.put.my_logger import MyLogger


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
                 logger,  # type: MyLogger
                 ):
        self.trash_dir = trash_dir
        self.trashing_checker = trashing_checker
        self.info_dir = info_dir
        self.security_check = SecurityCheck(fs)
        self.persister = persister
        self.dir_creator = TrashDirCreator(fs)
        self.executor = JobExecutor(logger)

    class Result(NamedTuple('Result', [
        ('ok', bool),
        ('reason', FailureReason)
    ])):
        def succeeded(self):
            return self.ok

    def trash_file_in(self,
                      candidate,  # type: Candidate
                      log_data,  # type: LogData
                      environ,  # type: Environ
                      trashee,  # type: Trashee
                      ):  # type: (...) -> Result
        secure = self.security_check.check_trash_dir_is_secure(candidate)
        if secure.is_error():
            return make_error(secure)

        can_be_used = self.trashing_checker.file_could_be_trashed_in(
            trashee, candidate, environ)
        if can_be_used.is_error():
            return make_error(can_be_used)

        dirs_creation = self.dir_creator.make_candidate_dirs(candidate)
        if dirs_creation.is_error():
            return make_error(dirs_creation)

        trashinfo_data = self.info_dir.make_trashinfo_data(
            trashee.path, candidate)
        if trashinfo_data.is_error():
            return make_error(trashinfo_data)

        persisting_job = self.persister.try_persist(trashinfo_data.value())
        trashed_file = self.executor.execute(persisting_job, log_data)
        trashed = self.trash_dir.try_trash(trashee.path, trashed_file)
        if trashed.is_error():
            return make_error(trashed)

        return make_ok()


def make_error(reason):  # type: (Left[FailureReason]) -> Janitor.Result
    return Janitor.Result(False, reason.error())


def make_ok():  # type: () -> Janitor.Result
    return Janitor.Result(True, NoLog())
