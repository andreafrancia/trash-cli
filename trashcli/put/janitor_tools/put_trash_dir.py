import os.path
from typing import NamedTuple

from trashcli.put.core.either import Either
from trashcli.put.core.either import Left
from trashcli.put.core.either import Right
from trashcli.put.core.failure_reason import FailureReason
from trashcli.put.core.failure_reason import LogContext
from trashcli.put.fs.fs import Fs
from trashcli.put.janitor_tools.info_file_persister import TrashedFile


class UnableToMoveFileToTrash(NamedTuple('UnableToMoveFileToTrash', [
    ('error', Exception),
]), FailureReason):
    def log_entries(self, context):  # type: (LogContext) -> str
        return "failed to move %s in %s: %s" % (
            context.trashee_path,
            context.files_dir(),
            self.error,
        )


class PutTrashDir:
    def __init__(self,
                 fs,  # type: Fs
                 ):
        self.fs = fs

    def try_trash(self,
                  path,  # type: str
                  paths,  # type: TrashedFile
                  ):  # type: (...) -> Either[None, Exception]
        try:
            move_file(self.fs, path, paths.backup_copy_path)
            return Right(None)
        except (IOError, OSError) as error:
            # the move can copy the file before failing to delete the original; drop the copy so no unremovable file is left in the trash
            if self.fs.lexists(paths.backup_copy_path):
                self.fs.remove_file(paths.backup_copy_path)
            self.fs.remove_file(paths.trashinfo_path)
            return Left(UnableToMoveFileToTrash(error))


def move_file(fs,  # type: Fs
              src, # type: str
              dest, # type: str
              ):
    # Using nornpath allow to delete symlink to a dir even if the are
    # specified with traling slash
    fs.move(os.path.normpath(src), dest)
