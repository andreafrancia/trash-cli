from trashcli.fstab.volume_of import VolumeOf
from trashcli.put.fs.parent_realpath import ParentRealpathFs


class VolumeOfParent:
    def __init__(self,
                 volumes,  # type: VolumeOf
                 parent_realpath_fs,  # type: ParentRealpathFs
                 ):
        self.volumes = volumes
        self.parent_realpath_fs = parent_realpath_fs

    def volume_of_parent(self, path):
        parent_realpath = self.parent_realpath_fs.parent_realpath(path)
        return self.volumes.volume_of(parent_realpath)
