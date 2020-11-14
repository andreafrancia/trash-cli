# Copyright (C) 2009-2020 Andrea Francia Trivolzio(PV) Italy
def main():
    for mp in mount_points():
        print(mp)


def mount_points():
    import psutil
    for p in psutil.disk_partitions():
        yield p.mountpoint


if __name__ == "__main__":
    main()
