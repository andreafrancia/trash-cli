from trashcli.fstab.os.os_mount_points import os_mount_points
from trashcli.fstab.list_mount_points_fs import OsMountPointsFs


class FakeOsMountPointsFs(OsMountPointsFs):
    def __init__(self, mount_points):
        self.mount_points = mount_points

    def list_os_mount_points(self):
        return self.mount_points
