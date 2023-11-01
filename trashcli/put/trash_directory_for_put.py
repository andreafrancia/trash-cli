from typing import NamedTuple

from trashcli.put.core.either import Either, Right, Left
from trashcli.put.core.failure_reason import FailureReason, LogEntry, Level
from trashcli.put.fs.fs import Fs
from trashcli.put.info_dir import InfoDir2
from trashcli.put.info_dir import TrashedFile


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


class TrashDirectoryForPut:
    def __init__(self,
                 fs,  # type: Fs
                 info_dir2,  # type: InfoDir2
                 ):
        self.fs = fs
        self.info_dir2 = info_dir2

    def try_trash(self,
                  path,  # type: str
                  paths,  # type: TrashedFile
                  ):  # type: (...) -> Either[None, Exception]
        try:
            self.fs.move(path, paths.backup_copy_path)
            return Right(None)
        except (IOError, OSError) as error:
            self.fs.remove_file(paths.trashinfo_path)
            return Left(UnableToMoveFileToTrash(error))
