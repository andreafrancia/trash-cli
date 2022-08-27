import unittest

from trashcli.list_mount_points import Partitions


class MockPartition:
    def __init__(self, **kwargs):
        self.__dict__ = kwargs


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
