import unittest

from trashcli.empty.parse_reply import parse_reply


class TestParseReply(unittest.TestCase):
    def test_y(self):
        assert parse_reply('y') == True

    def test_Y(self):
        assert parse_reply('Y') == True

    def test_n(self):
        assert parse_reply('n') == False

    def test_N(self):
        assert parse_reply('N') == False

    def test_empty_string(self):
        assert parse_reply('') == False
