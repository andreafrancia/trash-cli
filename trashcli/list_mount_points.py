# Copyright (C) 2009-2020 Andrea Francia Trivolzio(PV) Italy
import os.path


def os_mount_points():
    import psutil
    # List of accepted non-physical fstypes
    fstypes = [
        'nfs',
        'nfs4',
        'p9', # file system used in WSL 2 (Windows Subsystem for Linux)
        'btrfs',
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
