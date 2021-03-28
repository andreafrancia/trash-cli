import unittest

from trashcli.list import decide_trash_dirs
from trashcli.trash import TrashDirsScanner


class Test_decide_trash_dirs(unittest.TestCase):
    def test_default(self):

        result = list(decide_trash_dirs([], ['system-dirs']))

        assert result == ['system-dirs']

    def test_user_specified(self):

        result = list(decide_trash_dirs(['user-specified-dirs'], ['system-dirs']))

        assert result == [(TrashDirsScanner.Found, ('user-specified-dirs', '/'))]
