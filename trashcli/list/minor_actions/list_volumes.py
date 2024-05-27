from __future__ import print_function

from trashcli.fstab.mount_points_listing import MountPointsListing
from trashcli.fstab.volume_listing import ListingConfig
from trashcli.fstab.volume_listing import VolumesListing


class PrintVolumesArgs(object):
    pass


class PrintVolumesList(object):
    def __init__(self,
                 environ,
                 out,
                 mount_points_listing,  # type: MountPointsListing
                 ):
        self.environ = environ
        self.out = out
        self.mount_points_listing = mount_points_listing

    def run_action(self,
                   args,  # type: PrintVolumesArgs
                   ):
        volumes_listing_config = ListingConfig(self.environ)
        volume_listing = VolumesListing(self.mount_points_listing)
        for volume in volume_listing.list_volumes(volumes_listing_config):
            print(volume, file=self.out)
