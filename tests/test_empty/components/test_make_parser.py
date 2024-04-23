import unittest
from typing import Union

from trashcli.empty.parser import Parser


class TestMakeParser(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def test(self):
        parsed = self.parse(args=['--trash-dir=foo'])

        assert ['foo'] == parsed.user_specified_trash_dirs

    def test_non_interactive_default_is_non_interactive(self):
        parsed = self.parse(default_is_interactive=False,
                                   args=[])

        assert parsed.interactive == False

    def test_interactive_default_is_interactive(self):
        parsed = self.parse(default_is_interactive=True,
                                   args=[])

        assert parsed.interactive == True

    def test_interactive_made_non_interactive(self):
        parsed = self.parse(default_is_interactive=True, args=['-f'])

        assert parsed.interactive == False

    def test_dry_run(self):
        parsed = self.parse(args=['--dry-run'])

        assert parsed.dry_run == True

    def test_dry_run_default(self):
        parsed = self.parse(args=[])

        assert parsed.dry_run == False

    def parse(self,
              args,
              default_is_interactive="ignored",  # type: Union[bool, str]
              ):
        return self.parser.parse(default_is_interactive=default_is_interactive,
                                 args=args,
                                 environ={},
                                 uid=0,
                                 argv0="ignored",)
