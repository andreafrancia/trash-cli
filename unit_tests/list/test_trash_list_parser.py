import unittest

import trashcli.list


class TestTrashListParser(unittest.TestCase):
    def setUp(self):
        self.parser = trashcli.list.parser()

    def test_version(self):

        parsed = self.parser.parse_args(['--version'])

        assert True == parsed.version

    def test_help(self):

        parsed = self.parser.parse_args(['--help'])

        assert True == parsed.help
