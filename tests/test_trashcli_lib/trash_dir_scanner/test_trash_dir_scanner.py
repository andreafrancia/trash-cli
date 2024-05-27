import unittest

from tests.support.py2mock import Mock

from trashcli.fstab.mount_points_listing import FakeMountPointsListing
from trashcli.lib.dir_checker import DirChecker
from trashcli.lib.user_info import SingleUserInfoProvider
from trashcli.trash_dirs_scanner import TrashDirsScanner
from trashcli.trash_dirs_scanner import trash_dir_found


class TestTrashDirScanner(unittest.TestCase):
    def test_scan_trash_dirs(self):
        user_info_provider = SingleUserInfoProvider()
        dir_checker = Mock(spec=DirChecker)
        scanner = TrashDirsScanner(
            user_info_provider,
            top_trash_dir_rules=Mock(),
            dir_checker=dir_checker,
            mount_points_listing=FakeMountPointsListing(['/vol', '/vol2']),
        )

        dir_checker.is_dir.return_value = True
        result = list(scanner.scan_trash_dirs({'HOME': '/home/user'}, 123))

        self.assertEqual(
            [(trash_dir_found, ('/home/user/.local/share/Trash', '/')),
             (trash_dir_found, ('/vol/.Trash-123', '/vol')),
             (trash_dir_found, ('/vol2/.Trash-123', '/vol2'))], result)
