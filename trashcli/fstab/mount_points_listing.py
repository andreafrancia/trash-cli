# Copyright (C) 2009-2020 Andrea Francia Trivolzio(PV) Italy
from trashcli.fstab.protocols.mount_point_list_fs import MountPointListFs
from trashcli.fstab.real.os_mount_points import os_mount_points


class RealMountPointListFs(MountPointListFs):
    def list_mount_points(self):
        return os_mount_points()
