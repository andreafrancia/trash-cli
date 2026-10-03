from typing import Any, List, NamedTuple

from trashcli.fstab.protocols.disk_partitions_fs import DiskPartitionsFs

FakePartition = NamedTuple('FakePartition', [
    ('device', str),
    ('mountpoint', str),
    ('fstype', str),
])


class FakeDiskPartitionsFs(DiskPartitionsFs):
    def __init__(self):
        self.physical = []  # type: List[FakePartition]
        self.virtual = []  # type: List[FakePartition]

    def add_physical(self, device, mountpoint, fstype):
        self.physical.append(FakePartition(device, mountpoint, fstype))

    def add_virtual(self, device, mountpoint, fstype):
        self.virtual.append(FakePartition(device, mountpoint, fstype))

    def disk_partitions(self,
                        all,  # type: bool
                        ):  # type: (...) -> List[Any]
        if all:
            return self.physical + self.virtual
        return list(self.physical)
