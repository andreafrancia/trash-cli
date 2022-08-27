# Copyright (C) 2009-2020 Andrea Francia Trivolzio(PV) Italy
import os.path


def os_mount_points():
    import psutil
    # List of accepted non-physical fstypes
    fstypes = [
        'nfs',
        'p9', # file system used in WSL 2 (Windows Subsystem for Linux)
    ]

    # Append fstypes of physicial devices to list
    fstypes += set([p.fstype for p in psutil.disk_partitions()])

    for p in psutil.disk_partitions(all=True):
        if os.path.isdir(p.mountpoint) and p.fstype in fstypes:
            yield p.mountpoint
