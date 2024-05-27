from trashcli.fstab.mount_points_listing import FakeMountPointsListing
from trashcli.fstab.volume_listing import ListingConfig
from trashcli.fstab.volume_listing import VolumesListing
from trashcli.lib.environ import Environ


class TestVolumesListing:
    def list_volumes_when_environ(self,
                                  environ,  # type: Environ
                                  ):
        mount_points_listing = FakeMountPointsListing(['/os-vol1', '/os-vol2'])
        volumes_listing = VolumesListing(mount_points_listing)
        volumes_listing_config = ListingConfig(environ)
        return volumes_listing.list_volumes(volumes_listing_config)

    def test_os_mount_points(self):
        result = self.list_volumes_when_environ({})

        assert result == ['/os-vol1', '/os-vol2']

    def test_one_vol_from_environ(self):
        result = self.list_volumes_when_environ({'TRASH_VOLUMES': '/fake-vol1'})

        assert result == ['/fake-vol1']

    def test_multiple_vols_from_environ(self):
        result = self.list_volumes_when_environ(
            {'TRASH_VOLUMES': '/fake-vol1:/fake-vol2:/fake-vol3'})

        assert result == ['/fake-vol1', '/fake-vol2', '/fake-vol3']

    def test_empty_environ(self):
        result = self.list_volumes_when_environ({'TRASH_VOLUMES': ''})

        assert result == ['/os-vol1', '/os-vol2']

    def test_skip_empty_vol(self):
        result = self.list_volumes_when_environ(
            {'TRASH_VOLUMES': '/vol1::/vol2'})

        assert result == ['/vol1', '/vol2']
