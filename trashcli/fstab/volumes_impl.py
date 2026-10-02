from trashcli.fstab.protocols.mount_point_list_fs import MountPointListFs
from trashcli.fslib.protocols.volumes_fs import VolumesFs
from trashcli.fslib.protocols.volume_of import VolumeOfFs


class VolumesFsImpl(VolumesFs):
    def __init__(self,
                 volumes,  # type: VolumeOfFs
                 mount_point_listing,  # type: MountPointListFs
                 ):
        self.volumes = volumes
        self.mount_point_listing = mount_point_listing

    def volume_of(self, path):
        return self.volumes.volume_of(path)

    def list_mount_points(self):
        return self.mount_point_listing.list_mount_points()
