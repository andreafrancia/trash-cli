from trashcli.fstab import FakeFstab

from nose.tools import assert_equals
from nose.tools import istest
from unit_tests.tools import assert_items_equal

class TestFakeFstab:
    def setUp(self):
        self.fstab = FakeFstab()

    @istest
    def on_default(self):
        self.assert_mount_points_are('/')

    @istest
    def it_should_accept_fake_mount_points(self):
        self.fstab.add_mount('/fake')

        self.assert_mount_points_are('/', '/fake')

    @istest
    def root_is_not_duplicated(self):
        self.fstab.add_mount('/')

        self.assert_mount_points_are('/')

    @istest
    def test_something(self):
        fstab = FakeFstab()
        fstab.add_mount('/fake')
        assert_equals('/fake', fstab.volume_of('/fake/foo'))

    def assert_mount_points_are(self, *expected_mounts):
        expected_mounts = list(expected_mounts)
        actual_mounts = list(self.fstab.mount_points())
        assert_items_equal(expected_mounts, list(self.fstab.mount_points()),
                'Expected: %s\n'
                'Found: %s\n' % (expected_mounts, actual_mounts))

