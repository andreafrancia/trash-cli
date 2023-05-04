import os
from abc import ABCMeta, abstractmethod

import six

from trashcli.fstab.mount_points_listing import MountPointsListing, \
    RealMountPointsListing


@six.add_metaclass(ABCMeta)
class VolumesListing:
    @abstractmethod
    def list_volumes(self, environ): # type (dict) -> Iterable[str]
        raise NotImplementedError()


class RealVolumesListing(VolumesListing):
    def list_volumes(self, environ):
        return VolumesListingImpl(RealMountPointsListing()).list_volumes(environ)


class VolumesListingImpl:
    def __init__(self,
                 mount_points_listing,  # type: MountPointsListing
                 ):
        self.mount_points_listing = mount_points_listing

    def list_volumes(self, environ):
        if 'TRASH_VOLUMES' in environ and environ['TRASH_VOLUMES']:
            return [vol
                    for vol in environ['TRASH_VOLUMES'].split(':')
                    if vol != '']
        return self.mount_points_listing.list_mount_points()


class NoVolumesListing(VolumesListing):
    def list_volumes(self, environ):
        return []


class RealIsMount:
    def is_mount(self, path):
        return os.path.ismount(path)
