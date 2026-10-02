import unittest
from tests.support.fakes.fake_volume_of import FakeVolumeOfFs


class TestFakeFstab(unittest.TestCase):

    def test_default(self):
        volumes = FakeVolumeOfFs()
        assert ["/"] == only_mount_points(volumes, ["/"])

    def test_it_should_accept_fake_mount_points(self):
        volumes = FakeVolumeOfFs()
        volumes.add_volume('/fake')
        assert ['/', '/fake'] == only_mount_points(volumes, ['/', '/fake'])

    def test_something(self):
        volumes = FakeVolumeOfFs()
        volumes.add_volume("/fake")
        assert '/fake' == volumes.volume_of('/fake/foo')


def only_mount_points(volumes, paths):
    return [p for p in paths if p == volumes.volume_of(p)]
