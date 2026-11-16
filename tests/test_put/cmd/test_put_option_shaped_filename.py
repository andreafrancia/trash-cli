import unittest

import pytest

from trashcli.lib.exit_codes import BAD_OPTION
from tests.support.dirs.support_fs import SupportFs
from tests.support.dirs.temp_dir import make_temp_dir
from trashcli.fslib.real.real_fs import RealFs
from trashcli.put.parser import Parser, ExitWithCode, Trash


@pytest.mark.slow
class TestPutOptionShapedFilename(unittest.TestCase):
    def setUp(self):
        fs = RealFs()
        self.temp_dir = make_temp_dir(fs)
        self.support_fs = SupportFs(fs, self.temp_dir)
        self.parser = Parser(fs)

    def test_it_refuses_an_existing_file_that_looks_like_an_option(self):
        self.support_fs.touch('--trash-dir=evil')

        result = self.parser.parse_args(['trash-put', '--trash-dir=evil'])

        assert result.type == ExitWithCode
        assert result.exit_code == BAD_OPTION

    def test_the_double_dash_separator_still_lets_you_trash_such_a_file(self):
        self.support_fs.touch('--trash-dir=evil')

        result = self.parser.parse_args(
            ['trash-put', '--', '--trash-dir=evil'])

        assert result.type is Trash
        assert result.files == ['--trash-dir=evil']

    def test_a_real_option_is_unaffected_when_no_such_file_exists(self):
        self.support_fs.touch('--trash-dir=evil')

        result = self.parser.parse_args(
            ['trash-put', '--trash-dir=/tmp/dir', 'foo'])

        assert result.type is Trash
        assert result.trash_dir == '/tmp/dir'

    def tearDown(self):
        self.temp_dir.clean_up()
