import unittest

from tests.support.fake_volumes import make_fake_volumes_from


class TestFakeFstab(unittest.TestCase):

    def test_default(self):
        self.volumes = make_fake_volumes_from([])
        assert ["/"] == self.filter_only_mount_points("/")

    def test_it_should_accept_fake_mount_points(self):
        self.volumes = make_fake_volumes_from(['/fake'])
        assert ['/', '/fake'] == self.filter_only_mount_points('/', '/fake')

    def test_something(self):
        volumes = make_fake_volumes_from(['/fake'])
        assert '/fake' == volumes.volume_of('/fake/foo')

    def filter_only_mount_points(self, *supposed_mount_points):
        return [mp for mp in supposed_mount_points
                if mp == self.volumes.volume_of(mp)]
