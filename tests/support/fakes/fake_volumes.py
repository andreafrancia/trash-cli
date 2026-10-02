import os

from trashcli.fstab.volumes import Volumes


class FakeVolumes(Volumes):
    def __init__(self,
                 mount_points,  # type Iterable[str]
                 ):
        self.mount_points = mount_points

    def list_mount_points(self):
        return self.mount_points

    def volume_of(self, path):
        while path != os.path.dirname(path):
            if self.is_a_mount_point(path):
                break
            path = os.path.dirname(path)
        return path

    def is_a_mount_point(self, path):
        return path in self.mount_points

    def add_volume(self, path):
        self.mount_points.append(path)
