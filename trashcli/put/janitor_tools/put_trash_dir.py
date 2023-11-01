from typing import NamedTuple

from trashcli.put.core.either import Either, Right, Left
from trashcli.put.core.failure_reason import FailureReason
from trashcli.put.core.failure_reason import LogContext
from trashcli.put.fs.fs import Fs
from trashcli.put.janitor_tools.info_creator import \
    TrashInfoCreator
from trashcli.put.janitor_tools.info_file_persister import TrashedFile


class UnableToMoveFileToTrash(NamedTuple('UnableToMoveFileToTrash', [
    ('error', Exception),
]), FailureReason):
    def log_entries(self, context):  # type: (LogContext) -> str
        return "failed to move %s in %s: %s" % (
            context.trashee_path,
            context.files_dir(),
            self.error)


class PutTrashDir:
    def __init__(self,
                 fs,  # type: Fs
                 info_dir2,  # type: TrashInfoCreator
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
