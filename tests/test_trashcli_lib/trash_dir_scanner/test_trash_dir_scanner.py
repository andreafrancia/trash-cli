from tests.support.fake_fs.fake_volumes_listing import FakeVolumesListing
from tests.support.py2mock import Mock

from trashcli.fslib.protocols.path_is_dir import PathIsDir
from trashcli.lib.single_user_info_provider import SingleUserInfoProvider
from trashcli.trash_dirs_scanner import TrashDirsScanner, trash_dir_found


class TestTrashDirScanner:
    def test_scan_trash_dirs(self):
        volumes_listing = FakeVolumesListing(['/vol', '/vol2'])
        user_info_provider = SingleUserInfoProvider()
        dir_checker = Mock(spec=PathIsDir)
        scanner = TrashDirsScanner(
            user_info_provider,
            volumes_listing=volumes_listing,
            top_trash_dir_rules=Mock(),
            dir_checker=dir_checker
        )

        dir_checker.path_isdir.return_value = True
        result = sorted(scanner.scan_trash_dirs({'HOME': '/home/user'}, 123))

        assert result == \
            [(trash_dir_found, ('/home/user/.local/share/Trash', '/')),
             (trash_dir_found, ('/vol/.Trash-123', '/vol')),
             (trash_dir_found, ('/vol2/.Trash-123', '/vol2'))]
