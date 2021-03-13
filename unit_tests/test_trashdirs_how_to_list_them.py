import unittest

from trashcli.trash import TrashDirs
from mock import Mock


class TestListTrashinfo(unittest.TestCase):
    def test_howto_list_trashdirs(self):
        environ = {'HOME':'/home/user'}
        trashdirs = TrashDirs(
                environ = environ,
                getuid = lambda:123,
                list_volumes = lambda:['/vol', '/vol2'],
                top_trash_dir_rules= Mock(),
                )

        result = list(trashdirs.scan_trash_dirs())

        self.assertEqual([(TrashDirs.Found, ('/home/user/.local/share/Trash', '/')),
                          (TrashDirs.Found, ('/vol/.Trash-123', '/vol')),
                          (TrashDirs.Found, ('/vol2/.Trash-123', '/vol2'))], result)
