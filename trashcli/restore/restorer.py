import os

from trashcli.restore.fs.restore_fs import RestoreFs
from trashcli.restore.trashed_file import TrashedFile


class Restorer:
    def __init__(self,
                 fs, # type: RestoreFs
                 ):
        self.read_fs = fs
        self.write_fs = fs

    def restore_trashed_file(self,
                             trashed_file, # type: TrashedFile
                             overwrite, # type: bool
                             ):
        """
        If overwrite is enabled, then the restore functionality will overwrite an existing file
        """
        if not overwrite and self.read_fs.exists(trashed_file.original_location):
            raise IOError(
                'Refusing to overwrite existing file "%s".' % os.path.basename(
                    trashed_file.original_location))
        else:
            parent = os.path.dirname(trashed_file.original_location)
            self.write_fs.mkdirs(parent)

        self.write_fs.move(trashed_file.original_file, trashed_file.original_location)
        self.write_fs.remove_file(trashed_file.info_file)
