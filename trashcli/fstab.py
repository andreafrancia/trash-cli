import os


def volume_of(path) :
    func = VolumeOf(os.path.ismount, os.path.abspath)
    return func.volume_of(path)

class FakeFstab:
    def __init__(self, volumes):
        self.volume_of = VolumeOf(FakeIsMount(volumes),
                                  os.path.normpath).volume_of

class FakeIsMount:
    def __init__(self, mount_points):
        self.fakes = set(['/'])
        for mp in mount_points:
            self.fakes.add(mp)

    def __call__(self, path):
        if path == '/':
            return True
        path = os.path.normpath(path)
        if path in self.fakes:
            return True
        return False


class VolumeOf:
    def __init__(self, ismount, abspath):
        self.ismount = ismount
        self.abspath = abspath

    def volume_of(self, path):
        path = self.abspath(path)
        while path != os.path.dirname(path):
            if self.ismount(path):
                break
            path = os.path.dirname(path)
        return path
