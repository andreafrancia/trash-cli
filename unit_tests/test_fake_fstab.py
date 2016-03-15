from trashcli.fstab import FakeFstab

from nose.tools import assert_equal, istest

# Try Python 2 import; if ImportError occurs, use Python 3 import
try:
    from nose.tools import assert_items_equal
except ImportError:
    from nose.tools import assert_count_equal as assert_items_equal

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
        assert_equal('/fake', fstab.volume_of('/fake/foo'))

    def assert_mount_points_are(self, *expected_mounts):
        expected_mounts = list(expected_mounts)
        actual_mounts = list(self.fstab.mount_points())
        assert_items_equal(expected_mounts, list(self.fstab.mount_points()),
                'Expected: %s\n'
                'Found: %s\n' % (expected_mounts, actual_mounts))

