import os
from typing import List, Callable

from tests.support.fake_is_mount import FakeIsMount
from trashcli.fstab.volume_of import VolumeOf, VolumeOfImpl


def fake_volume_of(volumes): # type: (List[str]) -> VolumeOf
    return VolumeOfImpl(FakeIsMount(volumes), os.path.normpath)


def volume_of_stub(func=lambda x: "volume_of %s" % x): # type: (Callable[[str], str]) -> VolumeOf
    return _FakeVolumeOf(func)


class _FakeVolumeOf(VolumeOf):
    def __init__(self, volume_of_impl):
        self.volume_of_impl = volume_of_impl

    def volume_of(self, path):
        return self.volume_of_impl(path)
