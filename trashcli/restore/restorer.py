import os

from trashcli.restore.file_system import RestoreFileSystem
from trashcli.restore.trashed_file import TrashedFile


class Restorer(object):
    def __init__(self,
                 fs, # type: RestoreFileSystem
                 ):
        self.fs = fs

    def restore_trashed_file(self,
                             trashed_file, # type: TrashedFile
                             overwrite, # type: bool
                             ):
        """
        If overwrite is enabled, then the restore functionality will overwrite an existing file
        """
        if not overwrite and self.fs.path_exists(trashed_file.original_location):
            raise IOError(
                'Refusing to overwrite existing file "%s".' % os.path.basename(
                    trashed_file.original_location))
        else:
            parent = os.path.dirname(trashed_file.original_location)
            self.fs.mkdirs(parent)

        self.fs.move(trashed_file.original_file, trashed_file.original_location)
        self.fs.remove_file(trashed_file.info_file)
