# Copyright (C) 2009-2020 Andrea Francia Trivolzio(PV) Italy
import os.path


def os_mount_points():
    import psutil
    # List of accepted non-physical fstypes
    fstypes = [
        'nfs',
        'nfs4',
        'p9', # file system used in WSL 2 (Windows Subsystem for Linux)
    ]

    # Append fstypes of physical devices to list
    fstypes += set([p.fstype for p in psutil.disk_partitions()])

    partitions = Partitions(fstypes)

    for p in psutil.disk_partitions(all=True):
        partitions.should_used_by_trashcli(p)
        if os.path.isdir(p.mountpoint) and p.fstype in fstypes:
            yield p.mountpoint


class Partitions:
    def __init__(self, safe_list):
        self.safe_list = safe_list

    def should_used_by_trashcli(self, partition):
        return partition.fstype in self.safe_list
