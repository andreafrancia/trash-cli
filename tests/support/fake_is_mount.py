import os
from typing import List


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
