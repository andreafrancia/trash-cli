import os
from abc import ABCMeta, abstractmethod

import six

from trashcli.fslib.protocols.volumes_listing import VolumesListing
from trashcli.fstab.volumes_listing_impl import VolumesListingImpl
from trashcli.fstab.mount_points_listing import MountPointListFs, \
    RealMountPointListFs


class NoVolumesListing(VolumesListing):
    def list_volumes(self, environ):
        return []
