import os

from trashcli.put.fs.fs import RealPathFs


class TrashDirVolumeReader:
    def __init__(self,
                 fs,  # type: RealPathFs
                 ):
        self.fs = fs

    def volume_of_trash_dir(self, trash_dir_path):
        norm_trash_dir_path = os.path.normpath(trash_dir_path)
        return self.fs.volume_of(
            self.fs.realpath(norm_trash_dir_path))
