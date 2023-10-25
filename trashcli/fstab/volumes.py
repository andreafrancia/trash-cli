from abc import ABCMeta

import six
import os
from trashcli.fstab.mount_points_listing import MountPointsListing, \
    RealMountPointsListing
from trashcli.fstab.volume_of import VolumeOf, RealVolumeOf


@six.add_metaclass(ABCMeta)
class Volumes(VolumeOf, MountPointsListing):
    pass


class RealVolumes(Volumes):
    def volume_of(self, path):
        return RealVolumeOf().volume_of(path)

    def list_mount_points(self):
        return RealMountPointsListing().list_mount_points()


class VolumesImpl(Volumes):
    def __init__(self,
                 volumes,  # type: VolumeOf
                 mount_point_listing,  # type: MountPointsListing
                 ):
        self.volumes = volumes
        self.mount_point_listing = mount_point_listing

    def volume_of(self, path):
        return self.volumes.volume_of(path)

    def list_mount_points(self):
        return self.mount_point_listing.list_mount_points()


class FakeVolumes(Volumes):
    def __init__(self,
                 mount_points,  # type Iterable[str]
                 ):
        self.mount_points = mount_points

    def list_mount_points(self):
        return self.mount_points

    def volume_of(self, path):
        while path != os.path.dirname(path):
            if self.is_a_mount_point(path):
                break
            path = os.path.dirname(path)
        return path

    def is_a_mount_point(self, path):
        return path in self.mount_points

    def add_volume(self, path):
        self.mount_points.append(path)


class FakeVolumes2(Volumes):
    def __init__(self, volume_of_string, volumes_list):
        self.volume_of_string = volume_of_string
        self.volumes_list = volumes_list

    def volume_of(self, path):
        return self.volume_of_string % path

    def set_volumes(self, volumes_list):
        self.volumes_list = volumes_list

    def list_mount_points(self):
        return self.volumes_list
