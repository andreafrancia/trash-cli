import unittest

from trashcli.put.core.mode import Mode
from trashcli.put.parser import make_parser


class Test_make_parser(unittest.TestCase):
    def setUp(self):
        self.parser = make_parser("program-name")

    def test(self):
        options = self.parser.parse_args([])

        assert options.verbose == 0

    def test2(self):
        options = self.parser.parse_args(['-v'])

        assert options.verbose == 1

    def test3(self):
        options = self.parser.parse_args(['-vv'])

        assert options.verbose == 2

    def test_trash_dir_not_specified(self):
        options = self.parser.parse_args([])

        assert options.trashdir is None

    def test_trash_dir_specified(self):
        options = self.parser.parse_args(['--trash-dir', '/MyTrash'])

        assert options.trashdir == '/MyTrash'

    def test_force_volume_off(self):
        options = self.parser.parse_args([])

        assert options.forced_volume is None

    def test_force_volume_on(self):
        options = self.parser.parse_args(['--force-volume', '/fake-vol'])

        assert options.forced_volume == '/fake-vol'

    def test_force_option_default(self):
        options = self.parser.parse_args([])

        assert options.mode == Mode.mode_unspecified

    def test_force_option(self):
        options = self.parser.parse_args(['-f'])

        assert options.mode == Mode.mode_force

    def test_interactive_override_force_option(self):
        options = self.parser.parse_args(['-f', '-i'])

        assert options.mode == Mode.mode_interactive

    def test_interactive_option(self):
        options = self.parser.parse_args(['-i'])

        assert options.mode == Mode.mode_interactive
