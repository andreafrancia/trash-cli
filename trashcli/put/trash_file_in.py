from typing import Tuple, NamedTuple, List

from trashcli.lib.environ import Environ
from trashcli.put.candidate import Candidate
from trashcli.put.core.failure_reason import FailureReason, LogEntry, Level, \
    LogContext
from trashcli.put.dir_maker import DirMaker
from trashcli.put.fs.fs import Fs
from trashcli.put.info_dir import InfoDir2
from trashcli.put.my_logger import LogData
from trashcli.put.reporter import TrashPutReporter
from trashcli.put.security_check import SecurityCheck
from trashcli.put.trash_directory_for_put import TrashDirectoryForPut
from trashcli.put.trashee import Trashee
from trashcli.put.trashing_checker import TrashDirChecker


class NoLog(FailureReason):
    def log_entries(self, context):  # type: (LogContext) -> List[LogEntry]
        return []


class TrashDirIsNotSecure(NamedTuple('TrashDirIsNotSecure', [
    ('trash_dir', Candidate),
]), FailureReason):
    def log_entries(self, context):  # type: (LogContext) -> List[LogEntry]
        return [LogEntry(Level.INFO,
                         "trash directory is not secure: %s" % self.trash_dir.norm_path())]


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
                 ):
        self.reporter = reporter
        self.trash_dir = trash_dir
        self.dir_maker = dir_maker
        self.trashing_checker = trashing_checker
        self.info_dir = info_dir
        self.security_check = SecurityCheck(fs)

    def trash_file_in(self,
                      candidate,  # type: Candidate
                      log_data,  # type: LogData
                      environ,  # type: Environ
                      trashee,  # type: Trashee
                      ):  # type: (...) -> Tuple[bool, FailureReason]
        trash_dir_is_secure, messages = self.security_check. \
            check_trash_dir_is_secure(candidate)
        self.reporter.log_info_messages(messages, log_data)

        if not trash_dir_is_secure:
            return False, TrashDirIsNotSecure(candidate)
        self.reporter.trash_dir_with_volume(candidate, log_data)

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

        trashinfo_ok, paths, error = self.info_dir.create_trashinfo_file(
            trashinfo_data)
        if not trashinfo_ok:
            # TODO: use a specific Log class
            self.reporter.unable_to_trash_file_in_because(
                trashee.path, candidate, error, log_data,
                environ)
            return False, NoLog()

        error = self.trash_dir.try_trash(trashee.path, paths)
        if error:
            self.reporter.unable_to_trash_file_in_because(
                trashee.path, candidate, error, log_data,
                environ)
            return False, NoLog()

        return True, NoLog()

    def _make_candidate_dirs(self, candidate):
        try:
            self.dir_maker.mkdir_p(candidate.trash_dir_path, 0o700)
            self.dir_maker.mkdir_p(candidate.files_dir(), 0o700)
            self.dir_maker.mkdir_p(candidate.info_dir(), 0o700)
            return True, None
        except (IOError, OSError) as error:
            return False, error
