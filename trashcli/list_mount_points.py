# Copyright (C) 2009-2020 Andrea Francia Trivolzio(PV) Italy
import os.path


def main():
    for mp in os_mount_points():
        print(mp)


def os_mount_points():
    import psutil
    for p in psutil.disk_partitions():
        if os.path.isdir(p.mountpoint):
            yield p.mountpoint


if __name__ == "__main__":
    main()
