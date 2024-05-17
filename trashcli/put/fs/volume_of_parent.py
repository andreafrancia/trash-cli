from trashcli.fstab.volume_of import VolumeOf
from trashcli.put.fs.parent_realpath import ParentRealpathFs


class VolumeOfParent:
    def __init__(self,
                 fs,  # type: VolumeOf
                 ):
        self.fs = fs

    def volume_of_parent(self, path):
        parent_realpath = ParentRealpathFs(self.fs).parent_realpath(path)
        return self.fs.volume_of(parent_realpath)
