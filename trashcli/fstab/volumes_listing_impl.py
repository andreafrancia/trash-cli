from trashcli.fstab.mount_points_listing import MountPointListFs


class VolumesListingImpl:
    def __init__(self,
                 mount_points_listing,  # type: MountPointListFs
                 ):
        self.mount_points_listing = mount_points_listing

    def list_volumes(self, environ):
        if 'TRASH_VOLUMES' in environ and environ['TRASH_VOLUMES']:
            return [vol
                    for vol in environ['TRASH_VOLUMES'].split(':')
                    if vol != '']
        return self.mount_points_listing.list_mount_points()
