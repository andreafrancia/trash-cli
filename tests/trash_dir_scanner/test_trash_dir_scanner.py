import unittest

from trashcli.trash import TrashDirsScanner, trash_dir_found, UserInfoProvider
from mock import Mock


class TestTrashDirScanner(unittest.TestCase):
    def test_scan_trash_dirs(self):
        environ = {'HOME':'/home/user'}
        user_info_provider = UserInfoProvider(environ, lambda:123)
        scanner = TrashDirsScanner(
                user_info_provider,
                list_volumes = lambda:['/vol', '/vol2'],
                top_trash_dir_rules= Mock(),
                )

        result = list(scanner.scan_trash_dirs())

        self.assertEqual(
            [(trash_dir_found, ('/home/user/.local/share/Trash', '/')),
             (trash_dir_found, ('/vol/.Trash-123', '/vol')),
             (trash_dir_found, ('/vol2/.Trash-123', '/vol2'))], result)
