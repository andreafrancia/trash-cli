import unittest

from trashcli.fstab import FakeFstab


class TestFakeFstab(unittest.TestCase):
    def setUp(self):
        self.fstab = FakeFstab()

    def test_default(self):
        assert ["/"] == self.filter_only_mount_points("/")

    def test_it_should_accept_fake_mount_points(self):
        self.fstab.add_mount('/fake')
        assert ['/', '/fake'] == self.filter_only_mount_points('/', '/fake')

    def test_something(self):
        fstab = FakeFstab()
        fstab.add_mount('/fake')
        assert '/fake' == fstab.volume_of('/fake/foo')

    def filter_only_mount_points(self, *supposed_mount_points):
        return [mp for mp in supposed_mount_points
                if mp == self.fstab.volume_of(mp)]
