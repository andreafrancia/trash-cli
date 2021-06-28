import unittest

from trashcli.list import decide_trash_dirs
from trashcli.trash import trash_dir_found


class Test_decide_trash_dirs(unittest.TestCase):
    def test_default(self):

        result = list(decide_trash_dirs(False, [], ['system-dirs']))

        assert result == ['system-dirs']

    def test_user_specified(self):

        result = list(decide_trash_dirs(False, ['user-specified-dirs'], ['system-dirs']))

        assert result == [(trash_dir_found, ('user-specified-dirs', '/'))]
