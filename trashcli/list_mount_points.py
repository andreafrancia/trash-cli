# Copyright (C) 2009-2020 Andrea Francia Trivolzio(PV) Italy
import os.path


def main():
    for mp in os_mount_points():
        print(mp)

def os_mount_points():
    import psutil
    # List of accepted non-physical fstypes
    fstypes = ['nfs']

    # Append fstypes of physicial devices to list
    fstypes += set([p.fstype for p in psutil.disk_partitions()])

    for p in psutil.disk_partitions(all=True):
        if os.path.isdir(p.mountpoint) and p.fstype in fstypes:
            yield p.mountpoint

if __name__ == "__main__":
    main()
