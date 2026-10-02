from trashcli.fslib.real.real_abspath_fs import RealAbspathFs
from trashcli.fslib.real.real_is_mount import RealIsMount
from trashcli.fslib.protocols.volume_of import VolumeOfFs
from trashcli.fstab.volume_of_fs_impl import VolumeOfFsImpl


class RealVolumeOfFs(VolumeOfFs):
    def __init__(self):
        self.impl = VolumeOfFsImpl(RealIsMount(), RealAbspathFs())

    def volume_of(self, path):
        return self.impl.volume_of(path)
