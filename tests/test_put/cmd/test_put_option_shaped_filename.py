import unittest

from trashcli.lib.exit_codes import BAD_OPTION
from tests.support.dirs.my_path import MyPath
from trashcli.put.fs.real_fs import RealFs
from trashcli.put.parser import Parser, ExitWithCode, Trash


class TestPutOptionShapedFilename(unittest.TestCase):
    def setUp(self):
        self.cwd = MyPath.make_temp_dir()
        fs = RealFs()
        self.parser = Parser(fs)

    def test_it_refuses_an_existing_file_that_looks_like_an_option(self):
        self.cwd.touch('--trash-dir=evil')

        result = self.parser.parse_args(['trash-put', '--trash-dir=evil'])

        assert result.type == ExitWithCode
        assert result.exit_code == BAD_OPTION

    def test_the_double_dash_separator_still_lets_you_trash_such_a_file(self):
        self.cwd.touch('--trash-dir=evil')

        result = self.parser.parse_args(
            ['trash-put', '--', '--trash-dir=evil'])

        assert result.type is Trash
        assert result.files == ['--trash-dir=evil']

    def test_a_real_option_is_unaffected_when_no_such_file_exists(self):
        self.cwd.touch('--trash-dir=evil')

        result = self.parser.parse_args(
            ['trash-put', '--trash-dir=/tmp/dir', 'foo'])

        assert result.type is Trash
        assert result.trash_dir == '/tmp/dir'

    def tearDown(self):
        self.cwd.clean_up()
