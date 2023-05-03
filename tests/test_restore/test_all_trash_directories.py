import unittest

from tests.support.fake_volumes import volumes_fake
from trashcli.list_mount_points import FakeMountPointsListing
from trashcli.restore.trash_directories import TrashDirectories1


class TestTrashDirectories(unittest.TestCase):
    def setUp(self):
        volumes = volumes_fake(lambda x: "volume_of(%s)" % x)
        environ = {'HOME': '~'}
        self.mount_points_listing = FakeMountPointsListing([])
        self.trash_directories = TrashDirectories1(self.mount_points_listing,
                                                   volumes, 123, environ)

    def test_list_all_directories(self):
        self.mount_points_listing.set_mount_points(['/', '/mnt'])

        result = list(self.trash_directories.all_trash_directories())

        assert ([
                    ('~/.local/share/Trash', 'volume_of(~/.local/share/Trash)'),
                    ('/.Trash/123', '/'),
                    ('/.Trash-123', '/'),
                    ('/mnt/.Trash/123', '/mnt'),
                    ('/mnt/.Trash-123', '/mnt')] ==
                result)
