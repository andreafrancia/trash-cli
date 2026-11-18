import unittest

from tests.support.py2mock import Mock

from trashcli.fslib.protocols.volumes_listing import VolumesListing
from trashcli.fslib.protocols.path_is_dir import PathIsDir
from trashcli.lib.single_user_info_provider import SingleUserInfoProvider
from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.trash_dirs_scanner import TrashDirsScanner, TopTrashDirRules, \
    trash_dir_found


class TestTrashDirScanner(unittest.TestCase):
    def test_scan_trash_dirs(self):
        volumes_listing = Mock(spec=VolumesListing)
        user_info_provider = SingleUserInfoProvider()
        dir_checker = Mock(spec=PathIsDir)
        scanner = TrashDirsScanner(
            user_info_provider,
            volumes_listing=volumes_listing,
            top_trash_dir_rules=Mock(),
            dir_checker=dir_checker
        )

        dir_checker.path_isdir.return_value = True
        volumes_listing.list_volumes.return_value = ['/vol', '/vol2']
        result = sorted(scanner.scan_trash_dirs({'HOME': '/home/user'}, 123))

        self.assertEqual(
            [(trash_dir_found, ('/home/user/.local/share/Trash', '/')),
             (trash_dir_found, ('/vol/.Trash-123', '/vol')),
             (trash_dir_found, ('/vol2/.Trash-123', '/vol2'))], result)

    def test_a_trash_dir_made_by_another_user_is_skipped(self):
        fs = FakeFs()
        fs.makedirs('/vol/.Trash-123')
        fs.geteuid = lambda: 123
        volumes_listing = Mock(spec=VolumesListing)
        volumes_listing.list_volumes.return_value = ['/vol']
        scanner = TrashDirsScanner(SingleUserInfoProvider(), volumes_listing,
                                   TopTrashDirRules(fs), fs)

        assert list(scanner.scan_trash_dirs({}, 123)) == []
