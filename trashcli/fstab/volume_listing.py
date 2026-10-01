import os
from abc import ABCMeta, abstractmethod

import six

from trashcli.fslib.protocols.volumes_listing import VolumesListing
from trashcli.fstab.volumes_listing_impl import VolumesListingImpl
from trashcli.fstab.mount_points_listing import MountPointListFs, \
    RealMountPointListFs


class FixedVolumesListing(VolumesListing):
    def __init__(self, volumes):
        self.volumes = volumes

    def list_volumes(self, _environ):
        return self.volumes


class RealVolumesListing(VolumesListing):
    def list_volumes(self, environ):
        return VolumesListingImpl(RealMountPointListFs()).list_volumes(
            environ)


class NoVolumesListing(VolumesListing):
    def list_volumes(self, environ):
        return []


class RealIsMount:
    def is_mount(self, path):
        return os.path.ismount(path)
