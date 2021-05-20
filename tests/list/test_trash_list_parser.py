import unittest

import trashcli.list
from trashcli.trash import PrintHelp
from six import StringIO


class TestTrashListParser(unittest.TestCase):
    def setUp(self):
        self.parser = trashcli.list.maker_parser("trash-list")

    def test_version(self):
        parsed = self.parser.parse_args(['--version'])

        assert True == parsed.version

    def test_trash_dir_not_specified(self):
        parsed = self.parser.parse_args([])

        assert [] == parsed.trash_dirs

    def test_trash_dir_specified(self):
        parsed = self.parser.parse_args(['--trash-dir=foo'])

        assert ['foo'] == parsed.trash_dirs

    def test_size_off(self):
        parsed = self.parser.parse_args([])

        assert 'deletion_date' == parsed.attribute_to_print

    def test_size_on(self):
        parsed = self.parser.parse_args(['--size'])

        assert 'size' == parsed.attribute_to_print

    def test_files_off(self):
        parsed = self.parser.parse_args([])

        assert False == parsed.show_files

    def test_files_on(self):
        parsed = self.parser.parse_args(['--files'])

        assert True == parsed.show_files


class TestPrintHelp(unittest.TestCase):
    def test(self):
        out = StringIO()
        help_printer = PrintHelp(trashcli.list.description, out)
        help_printer.my_print_help('trash-list')
        assert out.getvalue() == ('Usage: trash-list [OPTIONS...]\n'
                                  '\n'
                                  'List trashed files\n'
                                  '\n'
                                  'Options:\n'
                                  "  --version   show program's version number and exit\n"
                                  '  -h, --help  show this help message and exit\n'
                                  '\n'
                                  'Report bugs to https://github.com/andreafrancia/trash-cli/issues\n')
