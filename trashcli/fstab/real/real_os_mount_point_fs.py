from trashcli.fstab.os.os_mount_points import os_mount_points
from trashcli.fstab.list_mount_points_fs import OsMountPointsFs


class RealOsMountPointsFs(OsMountPointsFs):
    def list_os_mount_points(self):
        return os_mount_points()
