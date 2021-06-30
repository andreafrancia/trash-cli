import unittest

from trashcli.trash import UserInfoProvider


class TestUserInfoProvider(unittest.TestCase):
    def test_getuid(self):
        provider = UserInfoProvider({}, lambda: 123)

        info = provider.get_user_info()

        assert [123] == [i.uid for i in info]

    def test_home(self):
        provider = UserInfoProvider({'HOME':"~"}, lambda: 123)

        info = provider.get_user_info()

        assert [['~/.local/share/Trash']] == \
               [i.home_trash_dir_paths for i in info]
