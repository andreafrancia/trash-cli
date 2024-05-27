import os

from trashcli.fstab.mount_points_listing import MountPointsListing


class VolumesListing:
    def __init__(self,
                 mount_points_listing,  # type: MountPointsListing
                 ):
        self.mount_points_listing = mount_points_listing

    def list_volumes(self,
                     config,  # type: ListingConfig
                     ):
        if config.should_use_alternate_volumes():
            return config.alternate_volumes()
        return self.mount_points_listing.list_mount_points()


class ListingConfig:
    def __init__(self, environ):
        self.environ = environ

    def should_use_alternate_volumes(self):
        return ('TRASH_VOLUMES' in self.environ
                and self.environ['TRASH_VOLUMES'])

    def alternate_volumes(self):
        if not self.should_use_alternate_volumes():
            return []

        return [vol
                for vol in self.environ['TRASH_VOLUMES'].split(':')
                if vol != '']


class RealIsMount:
    def is_mount(self, path):
        return os.path.ismount(path)
