# Copyright (C) 2009-2020 Andrea Francia Trivolzio(PV) Italy
from trashcli.fstab.mount_points_listing import MountPointListFs


class FakeMountPointListFs(MountPointListFs):
    def __init__(self, mount_points):
        self.mount_points = mount_points

    def set_mount_points(self, mount_points):
        self.mount_points = mount_points

    def list_mount_points(self):
        return self.mount_points
