import unittest

from trashcli.fstab import VolumesListing
from trashcli.trash import TrashDirsScanner, trash_dir_found, UserInfoProvider
from mock import Mock


class TestTrashDirScanner(unittest.TestCase):
    def test_scan_trash_dirs(self):
        volumes_listing = Mock(spec=VolumesListing)
        environ = {'HOME': '/home/user'}
        user_info_provider = UserInfoProvider(environ, lambda: 123)
        scanner = TrashDirsScanner(
            user_info_provider,
            volumes_listing=volumes_listing,
            top_trash_dir_rules=Mock(),
        )

        volumes_listing.list_volumes.return_value = ['/vol', '/vol2']
        result = list(scanner.scan_trash_dirs({}))

        self.assertEqual(
            [(trash_dir_found, ('/home/user/.local/share/Trash', '/')),
             (trash_dir_found, ('/vol/.Trash-123', '/vol')),
             (trash_dir_found, ('/vol2/.Trash-123', '/vol2'))], result)
