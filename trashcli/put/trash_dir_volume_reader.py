import os

from trashcli.fstab.volume_of import VolumeOf
from trashcli.put.fs.fs import RealPathFs


class TrashDirVolumeReader:
    def __init__(self,
                 volumes,  # type: VolumeOf
                 fs,  # type: RealPathFs
                 ):
        self.volumes = volumes
        self.fs = fs

    def volume_of_trash_dir(self, trash_dir_path):
        norm_trash_dir_path = os.path.normpath(trash_dir_path)
        return self.volumes.volume_of(
            self.fs.realpath(norm_trash_dir_path))
