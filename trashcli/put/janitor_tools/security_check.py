import os
from typing import NamedTuple, List

from trashcli.put.candidate import Candidate
from trashcli.put.core.check_type import NoCheck, TopTrashDirCheck
from trashcli.put.core.either import Either, Right, Left
from trashcli.put.core.failure_reason import FailureReason, LogContext, \
    LogEntry, Level


class SecurityCheck:

    def __init__(self, fs):
        self.fs = fs

    def check_trash_dir_is_secure(self,
                                  candidate,  # type: Candidate
                                  ):  # type: (...) -> Either[None, TrashDirIsNotSecure]
        if candidate.check_type == NoCheck:
            return Right(None)
        if candidate.check_type == TopTrashDirCheck:
            parent = os.path.dirname(candidate.trash_dir_path)
            if not self.fs.isdir(parent):
                return _error_c(candidate,
                    "found unusable .Trash dir (should be a dir): %s" % parent)
            if self.fs.islink(parent):
                return _error_c(candidate,
                    "found unsecure .Trash dir (should not be a symlink): %s" % parent)
            if not self.fs.has_sticky_bit(parent):
                return _error_c(candidate,
                    "found unsecure .Trash dir (should be sticky): %s" % parent)
            return Right(None)
        raise Exception("Unknown check type: %s" % candidate.check_type)


def _error_c(candidate, message):
    return Left(TrashDirIsNotSecure(candidate, [message]))


class TrashDirIsNotSecure(NamedTuple('TrashDirIsNotSecure', [
    ('trash_dir', Candidate),
    ('messages', List[str]),
]), FailureReason):
    def log_entries(self, context):  # type: (LogContext) -> List[LogEntry]
        return [LogEntry(Level.INFO, m) for m in self.messages] + [
            LogEntry(Level.INFO,
                     "trash directory is not secure: %s" % self.trash_dir.norm_path())]
