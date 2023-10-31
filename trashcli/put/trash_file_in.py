from typing import Tuple, NamedTuple, List

from trashcli.lib.environ import Environ
from trashcli.put.candidate import Candidate
from trashcli.put.core.failure_reason import FailureReason, LogEntry, Level, \
    LogContext
from trashcli.put.dir_maker import DirMaker
from trashcli.put.fs.fs import Fs
from trashcli.put.info_dir import InfoDir2
from trashcli.put.info_dir import PersistingInfoDir
from trashcli.put.my_logger import LogData
from trashcli.put.reporter import TrashPutReporter
from trashcli.put.security_check import SecurityCheck
from trashcli.put.trash_directory_for_put import TrashDirectoryForPut
from trashcli.put.trashee import Trashee
from trashcli.put.trashing_checker import TrashDirChecker


class NoLog(FailureReason):
    def log_entries(self, context):  # type: (LogContext) -> List[LogEntry]
        return []


class TrashDirCannotBeUsed(NamedTuple('TrashDirCannotBeUsed', [
    ('reason', str),
]), FailureReason):
    def log_entries(self, context):  # type: (LogContext) -> List[LogEntry]
        return [LogEntry(Level.INFO, self.reason)]


class UnableToGetParentVolume(NamedTuple('UnableToCreateTrashInfo', [
    ('error', Exception),
]), FailureReason):
    def log_entries(self, context):
        return [
            LogEntry(Level.INFO,
                     "failed to trash %s in %s, because: %s" % (
                         context.trashee_path,
                         context.shrunk_candidate_path,
                         self.error)),
        ]


class UnableToMoveFileToTrash(NamedTuple('UnableToMoveFileToTrash', [
    ('error', Exception),
]), FailureReason):
    def log_entries(self, context):
        return [
            LogEntry(Level.INFO,
                     "failed to trash %s in %s, because: %s" % (
                         context.trashee_path,
                         context.shrunk_candidate_path,
                         self.error)),
        ]


class TrashDirCannotBeCreated(
    NamedTuple('TrashDirCannotBeCreated', [
        ('error', Exception),
    ]), FailureReason):
    def log_entries(self,
                    context):  # type: (LogContext) -> List[LogEntry]
        return [
            LogEntry(Level.INFO,
                     "failed to trash %s in %s, because: %s" % (
                         context.trashee_path,
                         context.shrunk_candidate_path,
                         self.error)),
        ]


class UnableToCreateTrashInfoContent(
    NamedTuple('UnableToCreateTrashInfoContent', [
        ('error', Exception),
    ]), FailureReason):
    def log_entries(self, context):
        return [
            LogEntry(Level.INFO,
                     "failed to trash %s in %s, because: %s" % (
                         context.trashee_path,
                         context.shrunk_candidate_path,
                         self.error)),
        ]


class UnableToCreateTrashInfoFile(
    NamedTuple('UnableToCreateTrashInfoFile', [
        ('error', Exception),
    ]), FailureReason):
    def log_entries(self, context):
        return [
            LogEntry(Level.INFO,
                     "failed to trash %s in %s, because: %s" % (
                         context.trashee_path,
                         context.shrunk_candidate_path,
                         self.error)),
        ]


class Janitor:
    def __init__(self,
                 fs,  # type: Fs
                 reporter,  # type: TrashPutReporter
                 trash_dir,  # type: TrashDirectoryForPut
                 trashing_checker,  # type: TrashDirChecker
                 dir_maker,  # type: DirMaker
                 info_dir,  # type: InfoDir2
                 persister,  # type: PersistingInfoDir
                 ):
        self.reporter = reporter
        self.trash_dir = trash_dir
        self.dir_maker = dir_maker
        self.trashing_checker = trashing_checker
        self.info_dir = info_dir
        self.security_check = SecurityCheck(fs)
        self.persister = persister

    def trash_file_in(self,
                      candidate,  # type: Candidate
                      log_data,  # type: LogData
                      environ,  # type: Environ
                      trashee,  # type: Trashee
                      ):  # type: (...) -> Tuple[bool, FailureReason]
        secure = self.security_check.check_trash_dir_is_secure(candidate)

        if secure.is_error():
            return False, secure.error()

        ok, reason = self.trashing_checker.file_could_be_trashed_in(
            trashee, candidate, environ)
        if not ok:
            return False, TrashDirCannotBeUsed(reason)
        ok, error = self._make_candidate_dirs(candidate)
        if not ok:
            return False, TrashDirCannotBeCreated(error)

        ok_data, trashinfo_data, error = self.info_dir.make_trashinfo_data(
            trashee.path,
            candidate,
            log_data)
        if not ok_data:
            return False, UnableToCreateTrashInfoContent(error)

        trashed_file = self.persister.create_trashinfo_file(trashinfo_data)
        error = self.trash_dir.try_trash(trashee.path, trashed_file)

        if error:
            return False, UnableToMoveFileToTrash(error)

        return True, NoLog()

    def _make_candidate_dirs(self, candidate):
        try:
            self.dir_maker.mkdir_p(candidate.trash_dir_path, 0o700)
            self.dir_maker.mkdir_p(candidate.files_dir(), 0o700)
            self.dir_maker.mkdir_p(candidate.info_dir(), 0o700)
            return True, None
        except (IOError, OSError) as error:
            return False, error
