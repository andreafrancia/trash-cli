import unittest

from trashcli.empty.parser import Parser


class TestMakeParser(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def test(self):
        parsed = self.parser.parse(default_is_interactive=False,
                                   args=['--trash-dir=foo'])

        assert ['foo'] == parsed.user_specified_trash_dirs

    def test_non_interactive_default_is_non_interactive(self):
        parsed = self.parser.parse(default_is_interactive=False,
                                   args=[])

        assert parsed.interactive == False

    def test_interactive_default_is_interactive(self):
        parsed = self.parser.parse(default_is_interactive=True,
                                   args=[])

        assert parsed.interactive == True

    def test_interactive_made_non_interactive(self):
        parsed = self.parser.parse(default_is_interactive=True,
                                   args=['-f'])

        assert parsed.interactive == False
