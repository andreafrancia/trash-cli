import sys

from trashcli.fstab.real.os_mount_points import os_mount_points


class FakePsutil(object):
    def __init__(self, physical, all_partitions):
        self.physical = physical
        self.all_partitions = all_partitions

    def disk_partitions(self, all=False):
        return self.all_partitions if all else self.physical


class FakePartition(object):
    def __init__(self, mountpoint, fstype):
        self.device = 'fixture-device'
        self.mountpoint = mountpoint
        self.fstype = fstype


def mount_points(monkeypatch, physical, all_partitions, existing):
    monkeypatch.setitem(sys.modules, 'psutil', FakePsutil(physical, all_partitions))
    monkeypatch.setattr('trashcli.fstab.real.os_mount_points.os.path.isdir',
                        lambda path: path in existing)
    return list(os_mount_points())


def test_os_mount_points__virtiofs_exists__should_include_it(monkeypatch):
    shared = FakePartition('/fixture-shared', 'virtiofs')
    assert mount_points(monkeypatch, [], [shared], ['/fixture-shared']) == ['/fixture-shared']


def test_os_mount_points__physical_ext4_exists__should_include_it(monkeypatch):
    physical = FakePartition('/fixture-root', 'ext4')
    assert mount_points(monkeypatch, [physical], [physical], ['/fixture-root']) == ['/fixture-root']


def test_os_mount_points__proc_exists__should_exclude_it(monkeypatch):
    pseudo = FakePartition('/fixture-proc', 'proc')
    assert mount_points(monkeypatch, [], [pseudo], ['/fixture-proc']) == []


def test_os_mount_points__virtiofs_missing__should_exclude_it(monkeypatch):
    missing = FakePartition('/fixture-missing', 'virtiofs')
    assert mount_points(monkeypatch, [], [missing], []) == []
