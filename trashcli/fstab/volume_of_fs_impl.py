import os

from trashcli.fslib.protocols.abspath_fs import AbspathFs
from trashcli.fslib.protocols.is_mount_fs import IsMountFs
from trashcli.fslib.protocols.volume_of import VolumeOfFs


class VolumeOfFsImpl(VolumeOfFs):
    def __init__(self,
                 is_mount_fs,  # type: IsMountFs
                 abspath_fs,  # type: AbspathFs
                 ):
        self.is_mount_fs = is_mount_fs
        self.abspath_fs = abspath_fs

    def volume_of(self, path):
        path = self.abspath_fs.abspath(path)
        while path != os.path.dirname(path):
            if self.is_mount_fs.is_mount(path):
                break
            path = os.path.dirname(path)
        return path
