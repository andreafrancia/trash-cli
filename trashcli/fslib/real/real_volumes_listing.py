from trashcli.fslib.protocols.volumes_listing import VolumesListing
from trashcli.fstab.real.real_mount_point_list_fs import RealMountPointListFs
from trashcli.fstab.volumes_listing_impl import VolumesListingImpl


class RealVolumesListing(VolumesListing):
    def list_volumes(self, environ):
        return VolumesListingImpl(RealMountPointListFs()).list_volumes(
            environ)
