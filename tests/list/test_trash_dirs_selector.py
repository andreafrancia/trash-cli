import unittest

from trashcli.list import TrashDirsSelector
from trashcli.trash import trash_dir_found


class TestTrashDirsSelector(unittest.TestCase):
    def setUp(self):
        self.volume_of = lambda x: "volume_of %s" % x
        self.selector = TrashDirsSelector(['current-user-dirs'],
                                          ['all-user-dirs'],
                                          self.volume_of)

    def test_default(self):

        result = list(self.selector.select(False, []))

        assert result == ['current-user-dirs']

    def test_user_specified(self):

        result = list(self.selector.select(False, ['user-specified-dirs']))

        assert result == [(trash_dir_found, ('user-specified-dirs',
                                             'volume_of user-specified-dirs'))]

    def test_all_user_specified(self):

        result = list(self.selector.select(True, ['user-specified-dirs']))

        assert result == ['all-user-dirs']
