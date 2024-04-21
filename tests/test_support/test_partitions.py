import unittest

from trashcli.fstab.mount_points_listing import Partitions


class MockPartition:
    def __init__(self, device=None, mountpoint=None, fstype=None):
        self.device = device
        self.mountpoint = mountpoint
        self.fstype = fstype


class TestOsMountPoints(unittest.TestCase):
    def setUp(self):
        self.partitions = Partitions(['realfs'])

    def test_a_physical_fs(self):
        result = self.partitions.should_used_by_trashcli(
            MockPartition(fstype='realfs'))

        assert True == result

    def test_virtual_fs(self):
        result = self.partitions.should_used_by_trashcli(
            MockPartition(fstype='virtual_fs'))

        assert False == result

    def test_tmpfs(self):
        result = self.partitions.should_used_by_trashcli(
            MockPartition(
                device='tmpfs',
                mountpoint='/tmp',
                fstype='tmpfs'))

        assert True == result
