import unittest

from trashcli.fstab import create_fake_volume_of


class TestFakeFstab(unittest.TestCase):

    def test_default(self):
        self.volumes = create_fake_volume_of([])
        assert ["/"] == self.filter_only_mount_points("/")

    def test_it_should_accept_fake_mount_points(self):
        self.volumes = create_fake_volume_of(['/fake'])
        assert ['/', '/fake'] == self.filter_only_mount_points('/', '/fake')

    def test_something(self):
        volumes = create_fake_volume_of(['/fake'])
        assert '/fake' == volumes.volume_of('/fake/foo')

    def filter_only_mount_points(self, *supposed_mount_points):
        return [mp for mp in supposed_mount_points
                if mp == self.volumes.volume_of(mp)]
