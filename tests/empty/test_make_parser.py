import unittest

from trashcli import empty


class TestMakeParser(unittest.TestCase):
    def setUp(self):
        self.parser_interactive = empty.make_parser(True)
        self.parser = empty.make_parser(False)

    def test(self):
        parsed = self.parser.parse_args(['--trash-dir=foo'])

        assert ['foo'] == parsed.user_specified_trash_dirs

    def test_non_interactive_default_is_non_interactive(self):
        parsed = self.parser.parse_args([])

        assert parsed.interactive == False

    def test_interactive_default_is_interactive(self):
        parsed = self.parser_interactive.parse_args([])

        assert parsed.interactive == True

    def test_interactive_made_non_interactive(self):
        parsed = self.parser_interactive.parse_args(['-f'])

        assert parsed.interactive == False