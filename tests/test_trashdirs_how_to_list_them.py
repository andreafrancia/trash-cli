import unittest

from trashcli.trash import TrashDirsScanner, trash_dir_found
from mock import Mock


class TestListTrashinfo(unittest.TestCase):
    def test_howto_list_trashdirs(self):
        environ = {'HOME':'/home/user'}
        scanner = TrashDirsScanner(
                environ = environ,
                getuid = lambda:123,
                list_volumes = lambda:['/vol', '/vol2'],
                top_trash_dir_rules= Mock(),
                )

        result = list(scanner.scan_trash_dirs())

        self.assertEqual(
            [(trash_dir_found, ('/home/user/.local/share/Trash', '/')),
             (trash_dir_found, ('/vol/.Trash-123', '/vol')),
             (trash_dir_found, ('/vol2/.Trash-123', '/vol2'))], result)
