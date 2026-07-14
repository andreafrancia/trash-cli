import os

from trashcli.restore.restore_fs import RestoreReaderFs, \
    RestoreWriterFs
from trashcli.restore.trashed_file import TrashedFile


class Restorer:
    def __init__(self,
                 read_fs, # type: RestoreReaderFs
                 write_fs, # type: RestoreWriterFs
                 ):
        self.read_fs = read_fs
        self.write_fs = write_fs

    def restore_trashed_file(self,
                             trashed_file, # type: TrashedFile
                             overwrite, # type: bool
                             ):
        """Restore the file, overwriting the destination only when overwrite is set."""
        dest = trashed_file.original_location
        # lexists() also sees a dangling symlink, and a file must never be merged onto a directory.
        if self.read_fs.path_lexists(dest) and (
                not overwrite or self.read_fs.path_isdir(dest)):
            raise IOError(
                'Refusing to overwrite existing file "%s".' % os.path.basename(dest))
        self.write_fs.mkdirs(os.path.dirname(dest))
        self.write_fs.move(trashed_file.original_file, dest)
        self.write_fs.remove_file(trashed_file.info_file)
