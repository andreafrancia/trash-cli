import os

from trashcli.fstab.impl.volume_of_impl import VolumeOfImpl
from trashcli.fstab.real.real_is_mount import RealIsMount
from trashcli.fstab.volumes import Volumes


class RealVolumeOf(Volumes):
    def volume_of(self, path):
        impl = VolumeOfImpl(RealIsMount(), os.path.abspath)
        return impl.volume_of(path)
