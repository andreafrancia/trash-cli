import os

def volume_of(path) :
    return Fstab().volume_of(path)

class AbstractFstab(object):
    def __init__(self, ismount):
        self.ismount = ismount
    def volume_of(self, path):
        volume_of = VolumeOf(ismount=self.ismount)
        return volume_of(path)
    def mount_points(self):
        return self.ismount.mount_points()

class Fstab(AbstractFstab):
    def __init__(self):
        AbstractFstab.__init__(self, OsIsMount())

class FakeFstab:
    def __init__(self):
        self.ismount = FakeIsMount()
        self.volume_of = VolumeOf(ismount = self.ismount)
        self.volume_of.abspath = os.path.normpath

    def mount_points(self):
        return self.ismount.mount_points()

    def volume_of(self, path):
        volume_of = VolumeOf(ismount=self.ismount)
        return volume_of(path)

    def add_mount(self, path):
        self.ismount.add_mount(path)

from trashcli.list_mount_points import mount_points as os_mount_points
class OsIsMount:
    def __call__(self, path):
        return os.path.ismount(path)
    def mount_points(self):
        return os_mount_points()

class FakeIsMount:
    def __init__(self):
        self.fakes = set(['/'])
    def add_mount(self, path):
        self.fakes.add(path)
    def __call__(self, path):
        if path == '/':
            return True
        path = os.path.normpath(path)
        if path in self.fakes:
            return True
        return False
    def mount_points(self):
        return self.fakes.copy()

class VolumeOf:
    def __init__(self, ismount):
        self._ismount = ismount
        import os
        self.abspath = os.path.abspath

    def __call__(self, path):
        path = self.abspath(path)
        while path != os.path.dirname(path):
            if self._ismount(path):
                break
            path = os.path.dirname(path)
        return path

