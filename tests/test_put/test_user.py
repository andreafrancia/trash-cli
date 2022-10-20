import unittest
from typing import cast

import flexmock
import mock

from trashcli.put.describer import Describer
from trashcli.put.user import (
    User,
    parse_user_reply,
    user_replied_no,
    user_replied_yes,
)


class TestUser(unittest.TestCase):
    def setUp(self):
        self.my_input = mock.Mock()
        self.my_input.return_value = "y"
        self.describer = flexmock.Mock(spec=Describer)
        self.describer.should_receive('describe').and_return("description!")

        self.user = User(self.my_input, cast(Describer, self.describer))

    def test_yes(self):
        result = self.user.ask_user_about_deleting_file('prg', "file")

        assert result == 'user_replied_yes'


class Test_parse_user_reply(unittest.TestCase):
    def test_y(self): assert parse_user_reply('y') == user_replied_yes
    def test_Y(self): assert parse_user_reply('Y') == user_replied_yes
    def test_n(self): assert parse_user_reply('n') == user_replied_no
    def test_N(self): assert parse_user_reply('N') == user_replied_no
    def test_other(self): assert parse_user_reply('other') == user_replied_no
