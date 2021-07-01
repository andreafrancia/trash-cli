import unittest

from trashcli import empty


class TestMakeParser(unittest.TestCase):
    def setUp(self):
        self.parser = empty.make_parser()

    def test(self):
        parsed = self.parser.parse_args(['--trash-dir=foo'])

        assert ['foo'] == parsed.user_specified_trash_dirs