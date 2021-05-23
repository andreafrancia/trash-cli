import unittest

from trashcli.put import get_option_parser


class Test_get_option_parser(unittest.TestCase):
    def setUp(self):
        self.parser = get_option_parser("program-name", 'stdout', 'stderr')

    def test(self):
        (options, args) = self.parser.parse_args([])

        assert options.verbose == 0

    def test2(self):
        (options, args) = self.parser.parse_args(['-v'])

        assert options.verbose == 1

    def test3(self):
        (options, args) = self.parser.parse_args(['-vv'])

        assert options.verbose == 2

    def test_trash_dir_not_specified(self):
        (options, args) = self.parser.parse_args([])

        assert options.trashdir == None

    def test_trash_dir_specified(self):
        (options, args) = self.parser.parse_args(['--trash-dir', '/MyTrash'])

        assert options.trashdir == '/MyTrash'
