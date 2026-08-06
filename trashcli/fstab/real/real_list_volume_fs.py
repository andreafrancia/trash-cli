from trashcli.fstab.real.real_os_mount_point_fs import RealOsMountPointsFs
from trashcli.fstab.list_volume_fs import ListVolumeFs
from trashcli.fstab.impl.volume_listing_impl import ListVolumesFsImpl


class RealListVolumeFs(ListVolumeFs):
    def list_volumes(self, environ):
        return ListVolumesFsImpl(RealOsMountPointsFs()).list_volumes(
            environ)
