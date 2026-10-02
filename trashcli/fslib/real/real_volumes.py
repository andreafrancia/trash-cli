from trashcli.fslib.protocols.volumes_fs import VolumesFs
from trashcli.fstab.real.real_mount_point_list_fs import RealMountPointListFs
from trashcli.fslib.real.real_volume_of import RealVolumeOfFs


class RealVolumesFs(VolumesFs):
    def volume_of(self, path):
        return RealVolumeOfFs().volume_of(path)

    def list_mount_points(self):
        return RealMountPointListFs().list_mount_points()
