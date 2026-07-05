import unittest

import trashcli.list
import trashcli.list.main
import trashcli.list.parser
from trashcli.lib.print_version import PrintVersionArgs


class TestTrashListParser(unittest.TestCase):
    def setUp(self):
        self.parser = trashcli.list.parser.Parser("trash-list")

    def test_version(self):
        args = self.parse(['--version'])

        assert PrintVersionArgs == type(args)

    def test_trash_dir_not_specified(self):
        args = self.parse([])

        assert [] == args.trash_dirs

    def test_trash_dir_specified(self):
        args = self.parse(['--trash-dir=foo'])

        assert ['foo'] == args.trash_dirs

    def test_size_off(self):
        args = self.parse([])

        assert 'deletion_date' == args.attribute_to_print

    def test_size_on(self):
        args = self.parse(['--size'])

        assert 'size' == args.attribute_to_print

    def test_files_off(self):
        args = self.parse([])

        assert False == args.show_files

    def test_files_on(self):
        args = self.parse(['--files'])

        assert True == args.show_files

    def test_show_non_trashinfo_off(self):
        args = self.parse([])

        assert False == args.show_non_trashinfo

    def test_show_non_trashinfo_on(self):
        args = self.parse(['--show-non-trashinfo'])

        assert True == args.show_non_trashinfo

    def parse(self, args):
        return self.parser.parse_list_args(args, 'trash-list')
