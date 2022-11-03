import os

from typing import List


def volume_of(path):
    return volumes.volume_of(path)


def create_fake_volume_of(volumes):
    return Volumes(FakeIsMount(volumes), os.path.normpath)


class RealIsMount:
    def is_mount(self, path):
        return os.path.ismount(path)


class FakeIsMount:
    def __init__(self,
                 mount_points,  # type: List[str]
                 ):
        self.mount_points = mount_points

    def is_mount(self, path):
        if path == '/':
            return True
        path = os.path.normpath(path)
        if path in self.mount_points_list():
            return True
        return False

    def mount_points_list(self):
        return set(['/'] + self.mount_points)

    def add_mount_point(self, path):
        self.mount_points.append(path)


class Volumes:
    def __init__(self, ismount, abspath):
        self.ismount = ismount
        self.abspath = abspath

    def volume_of(self, path):
        path = self.abspath(path)
        while path != os.path.dirname(path):
            if self.ismount.is_mount(path):
                break
            path = os.path.dirname(path)
        return path


volumes = Volumes(RealIsMount(), os.path.abspath)


class VolumesListing:
    def __init__(self, os_mount_points):
        self.os_mount_points = os_mount_points

    def list_volumes(self, environ):
        if 'TRASH_VOLUMES' in environ and environ['TRASH_VOLUMES']:
            return [vol
                    for vol in environ['TRASH_VOLUMES'].split(':')
                    if vol != '']
        return self.os_mount_points()
