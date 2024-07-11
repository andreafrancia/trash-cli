import unittest

from tests.support.py2mock import Mock

from trashcli.fstab.volume_listing import VolumesListing
from trashcli.lib.dir_checker import DirChecker
from trashcli.lib.user_info import SingleUserInfoProvider
from trashcli.trash_dirs_scanner import TrashDirsScanner, trash_dir_found


class TestTrashDirScanner(unittest.TestCase):
    def test_scan_trash_dirs(self):
        volumes_listing = Mock(spec=VolumesListing)
        user_info_provider = SingleUserInfoProvider()
        dir_checker = Mock(spec=DirChecker)
        scanner = TrashDirsScanner(
            user_info_provider,
            volumes_listing=volumes_listing,
            top_trash_dir_rules=Mock(),
            dir_checker=dir_checker
        )

        dir_checker.is_dir.return_value = True
        volumes_listing.list_volumes.return_value = ['/vol', '/vol2']
        result = list(scanner.scan_trash_dirs({'HOME': '/home/user'}, 123))

        self.assertEqual(
            [(trash_dir_found, ('/home/user/.local/share/Trash', '/')),
             (trash_dir_found, ('/vol/.Trash-123', '/vol')),
             (trash_dir_found, ('/vol2/.Trash-123', '/vol2'))], result)
