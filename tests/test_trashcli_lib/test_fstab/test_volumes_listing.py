import unittest

from tests.support.fakes.fake_mount_point_list_fs import FakeMountPointListFs
from trashcli.fstab.volumes_listing_impl import VolumesListingImpl


class TestVolumesListingImpl(unittest.TestCase):
    def setUp(self):
        self.volumes_listing = VolumesListingImpl(FakeMountPointListFs(['/os-vol1', '/os-vol2']))

    def test_os_mount_points(self):
        result = self.volumes_listing.list_volumes({})

        assert sorted(result) == ['/os-vol1', '/os-vol2']

    def test_one_vol_from_environ(self):
        result = self.volumes_listing.list_volumes({'TRASH_VOLUMES': '/fake-vol1'})

        assert sorted(result) == ['/fake-vol1']

    def test_multiple_vols_from_environ(self):
        result = self.volumes_listing.list_volumes({'TRASH_VOLUMES': '/fake-vol1:/fake-vol2:/fake-vol3'})

        assert sorted(result) == ['/fake-vol1', '/fake-vol2', '/fake-vol3']

    def test_empty_environ(self):
        result = self.volumes_listing.list_volumes({'TRASH_VOLUMES': ''})

        assert sorted(result) == ['/os-vol1', '/os-vol2']

    def test_skip_empty_vol(self):
        result = self.volumes_listing.list_volumes({'TRASH_VOLUMES': '/vol1::/vol2'})

        assert sorted(result) == ['/vol1', '/vol2']
