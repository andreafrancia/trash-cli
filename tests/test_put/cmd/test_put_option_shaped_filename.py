import pytest

from trashcli.lib.exit_codes import BAD_OPTION
from tests.support.dirs.support_fs import SupportFs
from trashcli.put.parser import Parser, ExitWithCode, Trash

from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.support.fs_fixture import real_fs_fixture

fs = real_fs_fixture
temp_dir = temp_dir_fixture

@pytest.mark.slow
class TestPutOptionShapedFilename:
    @pytest.fixture(autouse=True)
    def setup_fs(self, fs, temp_dir):
        fs = fs
        self.temp_dir = temp_dir
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
