from trashcli.fstab.protocols.volumes import Volumes
from trashcli.fstab.real.real_mount_point_list_fs import RealMountPointListFs
from trashcli.fstab.real_volume_of import RealVolumeOf


class RealVolumes(Volumes):
    def volume_of(self, path):
        return RealVolumeOf().volume_of(path)

    def list_mount_points(self):
        return RealMountPointListFs().list_mount_points()
