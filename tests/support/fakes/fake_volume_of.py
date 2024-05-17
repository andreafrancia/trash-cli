import os
from typing import List

from tests.support.fakes.fake_is_mount import FakeIsMount
from trashcli.fstab.volume_of import VolumeOf
from trashcli.fstab.volume_of_impl import VolumeOfImpl


class FakeVolumeOf(VolumeOf):
    def __init__(self):  # type: () -> None
        super(FakeVolumeOf, self).__init__()
        self.volumes = []  # type: List[str]

    def add_volume(self, volume):
        self.volumes.append(volume)

    def volume_of(self, path):
        impl = VolumeOfImpl(FakeIsMount(self.volumes), os.path.normpath)
        return impl.volume_of(path)
