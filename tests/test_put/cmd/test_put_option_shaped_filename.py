import os
import unittest

from tests.support.dirs.my_path import MyPath
from trashcli.put.parser import Parser, ExitWithCode, Trash


class TestPutOptionShapedFilename(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.old_cwd = os.getcwd()
        os.chdir(self.tmp_dir)
        self.parser = Parser()

    def test_it_refuses_an_existing_file_that_looks_like_an_option(self):
        open('--trash-dir=evil', 'w').close()

        result = self.parser.parse_args(['trash-put', '--trash-dir=evil'])

        self.assertIs(result.type, ExitWithCode)
        self.assertNotEqual(0, result.exit_code)

    def test_the_double_dash_separator_still_lets_you_trash_such_a_file(self):
        open('--trash-dir=evil', 'w').close()

        result = self.parser.parse_args(
            ['trash-put', '--', '--trash-dir=evil'])

        self.assertIs(result.type, Trash)
        self.assertEqual(['--trash-dir=evil'], result.files)

    def test_a_real_option_is_unaffected_when_no_such_file_exists(self):
        open('foo', 'w').close()

        result = self.parser.parse_args(
            ['trash-put', '--trash-dir=/tmp/dir', 'foo'])

        self.assertIs(result.type, Trash)
        self.assertEqual('/tmp/dir', result.trash_dir)

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.tmp_dir.clean_up()
