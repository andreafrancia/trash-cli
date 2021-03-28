import unittest

import trashcli.list


class TestTrashListParser(unittest.TestCase):
    def setUp(self):
        self.parser = trashcli.list.maker_parser(True)

    def test_version(self):

        parsed = self.parser.parse_args(['--version'])

        assert True == parsed.version

    def test_help(self):

        parsed = self.parser.parse_args(['--help'])

        assert True == parsed.help

    def test_trash_dir_not_specified(self):

        parsed = self.parser.parse_args([])

        assert [] == parsed.trash_dirs

    def test_trash_dir_specified(self):

        parsed = self.parser.parse_args(['--trash-dir=foo'])

        assert ['foo'] == parsed.trash_dirs
