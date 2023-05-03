import os

from tests.support.fake_is_mount import FakeIsMount
from trashcli.fstab.volumes import VolumesImpl, Volumes


def make_fake_volumes_from(volumes):
    return VolumesImpl(FakeIsMount(volumes), os.path.normpath)


def volumes_fake(func=lambda x: "volume_of %s" % x):
    return _FakeVolumes(func)


class _FakeVolumes(Volumes):
    def __init__(self, volume_of_impl):
        self.volume_of_impl = volume_of_impl

    def volume_of(self, path):
        return self.volume_of_impl(path)
