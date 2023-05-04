# Copyright (C) 2009-2020 Andrea Francia Trivolzio(PV) Italy
import os
from abc import ABCMeta, abstractmethod

import six


@six.add_metaclass(ABCMeta)
class MountPointsListing:
    @abstractmethod
    def list_mount_points(self):
        raise NotImplementedError()


class RealMountPointsListing(MountPointsListing):
    def list_mount_points(self):
        return os_mount_points()


class FakeMountPointsListing(MountPointsListing):
    def __init__(self, mount_points):
        self.mount_points = mount_points

    def set_mount_points(self, mount_points):
        self.mount_points = mount_points

    def list_mount_points(self):
        return self.mount_points


def os_mount_points():
    import psutil
    # List of accepted non-physical fstypes
    fstypes = [
        'nfs',
        'nfs4',
        'p9',  # file system used in WSL 2 (Windows Subsystem for Linux)
        'btrfs',
        'fuse',  # https://github.com/andreafrancia/trash-cli/issues/250
        'fuse.glusterfs',
        # https://github.com/andreafrancia/trash-cli/issues/255
        'fuse.mergerfs',
    ]

    # Append fstypes of physical devices to list
    fstypes += set([p.fstype for p in psutil.disk_partitions()])

    partitions = Partitions(fstypes)

    for p in psutil.disk_partitions(all=True):
        if os.path.isdir(p.mountpoint) and \
                partitions.should_used_by_trashcli(p):
            yield p.mountpoint


class Partitions:
    def __init__(self, physical_fstypes):
        self.physical_fstypes = physical_fstypes

    def should_used_by_trashcli(self, partition):
        if ((partition.device, partition.mountpoint,
             partition.fstype) ==
                ('tmpfs', '/tmp', 'tmpfs')):
            return True
        return partition.fstype in self.physical_fstypes
