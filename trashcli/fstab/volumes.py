from abc import ABCMeta

import six
import os

from trashcli.compat import Protocol
from trashcli.fstab.real.real_mount_point_list_fs import RealMountPointListFs
from trashcli.fstab.protocols.mount_point_list_fs import MountPointListFs
from trashcli.fstab.volume_of import VolumeOf
from trashcli.fstab.real_volume_of import RealVolumeOf


class Volumes(VolumeOf, MountPointListFs, Protocol):
    pass


class RealVolumes(Volumes):
    def volume_of(self, path):
        return RealVolumeOf().volume_of(path)

    def list_mount_points(self):
        return RealMountPointListFs().list_mount_points()


class VolumesImpl(Volumes):
    def __init__(self,
                 volumes,  # type: VolumeOf
                 mount_point_listing,  # type: MountPointListFs
                 ):
        self.volumes = volumes
        self.mount_point_listing = mount_point_listing

    def volume_of(self, path):
        return self.volumes.volume_of(path)

    def list_mount_points(self):
        return self.mount_point_listing.list_mount_points()
