import os

from trashcli.fstab.volume_listing import RealIsMount
from trashcli.fstab.volume_of import VolumeOf
from trashcli.fstab.volume_of_impl import VolumeOfImpl


class RealVolumeOf(VolumeOf):
    def __init__(self):
        self.impl = VolumeOfImpl(RealIsMount(), os.path.abspath)

    def volume_of(self, path):
        return self.impl.volume_of(path)
