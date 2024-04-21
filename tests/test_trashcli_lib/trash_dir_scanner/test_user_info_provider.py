import unittest

from trashcli.lib.user_info import SingleUserInfoProvider


class TestUserInfoProvider(unittest.TestCase):
    def setUp(self):
        self.provider = SingleUserInfoProvider()

    def test_getuid(self):

        info = self.provider.get_user_info({}, 123)

        assert [123] == [i.uid for i in info]

    def test_home(self):

        info = self.provider.get_user_info({'HOME':"~"}, 123)

        assert [['~/.local/share/Trash']] == \
               [i.home_trash_dir_paths for i in info]
