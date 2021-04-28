import unittest

from trashcli.put import get_option_parser


class Test_get_option_parser(unittest.TestCase):
    def setUp(self):
        self.parser = get_option_parser("program-name", 'stdout', 'stderr')

    def test(self):
        (options, args) = self.parser.parse_args([])

        assert options.verbose == None

    def test2(self):
        (options, args) = self.parser.parse_args(['-v'])

        assert options.verbose == True