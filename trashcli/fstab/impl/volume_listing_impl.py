from trashcli.fstab.list_mount_points_fs import OsMountPointsFs


class ListVolumesFsImpl:
    def __init__(self,
                 os_mount_points_fs,  # type: OsMountPointsFs
                 ):
        self.os_mount_points_fs = os_mount_points_fs

    def list_volumes(self, environ):
        if 'TRASH_VOLUMES' in environ and environ['TRASH_VOLUMES']:
            return [vol
                    for vol in environ['TRASH_VOLUMES'].split(':')
                    if vol != '']
        return self.os_mount_points_fs.list_os_mount_points()
