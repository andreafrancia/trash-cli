from typing import List

from tests.support.fakes.fake_is_mount import FakeIsMount
from tests.support.fakes.normpath_fs import NormpathFs
from trashcli.fslib.protocols.volume_of import VolumeOfFs
from trashcli.fstab.volume_of_fs_impl import VolumeOfFsImpl


class FakeVolumeOfFs(VolumeOfFs):
    def __init__(self):  # type: () -> None
        super(FakeVolumeOfFs, self).__init__()
        self.volumes = []  # type: List[str]

    def add_volume(self, volume):
        self.volumes.append(volume)

    def volume_of(self, path):
        impl = VolumeOfFsImpl(FakeIsMount(self.volumes), NormpathFs())
        return impl.volume_of(path)
