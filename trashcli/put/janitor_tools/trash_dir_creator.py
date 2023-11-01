from typing import NamedTuple, List

from trashcli.put.core.candidate import Candidate
from trashcli.put.core.either import Either, Right, Left
from trashcli.put.core.failure_reason import FailureReason, LogContext, \
    LogEntry, Level
from trashcli.put.dir_maker import DirMaker
from trashcli.put.fs.fs import Fs


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


class TrashDirCreator:
    def __init__(self, fs):  # type: (Fs) -> None
        self.dir_maker = DirMaker(fs)

    def make_candidate_dirs(self,
                            candidate):  # type: (Candidate) -> Either[None, TrashDirCannotBeCreated]
        try:
            self.dir_maker.mkdir_p(candidate.trash_dir_path, 0o700)
            self.dir_maker.mkdir_p(candidate.files_dir(), 0o700)
            self.dir_maker.mkdir_p(candidate.info_dir(), 0o700)
            return Right(None)
        except (IOError, OSError) as error:
            return Left(TrashDirCannotBeCreated(error))
