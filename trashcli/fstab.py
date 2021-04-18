import os


def volume_of(path) :
    return volumes.volume_of(path)


def create_fake_volume_of(volumes):
    return Volumes(FakeIsMount(volumes), os.path.normpath)


class RealIsMount:
    def is_mount(self, path):
        return os.path.ismount(path)


class FakeIsMount:
    def __init__(self, mount_points):
        self.fakes = set(['/'])
        for mp in mount_points:
            self.fakes.add(mp)

    def is_mount(self, path):
        if path == '/':
            return True
        path = os.path.normpath(path)
        if path in self.fakes:
            return True
        return False


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
