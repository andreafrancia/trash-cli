import unittest

import trashcli.list
import trashcli.list.main
import trashcli.list.parser
from trashcli.list.actions import Action


class TestTrashListParser(unittest.TestCase):
    def setUp(self):
        self.parser = trashcli.list.parser.Parser("trash-list")

    def test_version(self):
        parsed = self.parser.parse_list_args(['--version'])

        assert Action.print_version == parsed.action

    def test_trash_dir_not_specified(self):
        parsed = self.parser.parse_list_args([])

        assert [] == parsed.trash_dirs

    def test_trash_dir_specified(self):
        parsed = self.parser.parse_list_args(['--trash-dir=foo'])

        assert ['foo'] == parsed.trash_dirs

    def test_size_off(self):
        parsed = self.parser.parse_list_args([])

        assert 'deletion_date' == parsed.attribute_to_print

    def test_size_on(self):
        parsed = self.parser.parse_list_args(['--size'])

        assert 'size' == parsed.attribute_to_print

    def test_files_off(self):
        parsed = self.parser.parse_list_args([])

        assert False == parsed.show_files

    def test_files_on(self):
        parsed = self.parser.parse_list_args(['--files'])

        assert True == parsed.show_files
