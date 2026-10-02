from abc import ABCMeta

import six
import os

from trashcli.fstab.protocols.mount_point_list_fs import MountPointListFs
from trashcli.fstab.protocols.volumes import Volumes
from trashcli.fstab.volume_of import VolumeOf


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
