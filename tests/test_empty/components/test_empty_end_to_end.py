import pytest

from tests.support.dirs.my_path import MyPath
from tests.support.fs_fixture import real_fs_fixture
from trashcli import trash
from tests.support.help.help_reformatting import reformat_help_message
from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.support.run.run_command import run_command
from trashcli.fslib.protocols.fs import Fs

fs = real_fs_fixture
temp_dir = temp_dir_fixture


class TestEmptyEndToEnd:
    @pytest.fixture(autouse=True)
    def setup_fs(self, fs, temp_dir):  # type: (Fs, MyPath) -> None
        fs = fs
        self.tmp_dir = temp_dir

    def test_help(self):
        result = run_command(self.tmp_dir, "trash-empty", ['--help'])

        assert [result.reformatted_help(),
                result.stderr,
                result.exit_code] == [reformat_help_message("""\
usage: trash-empty [-h] [--print-completion {bash,zsh,tcsh}] [--version] [-v]
                   [--trash-dir TRASH_DIR] [--all-users] [-i] [-f] [--dry-run]
                   [days]

Purge trashed files.

positional arguments:
  days

options:
  -h, --help            show this help message and exit
  --print-completion {bash,zsh,tcsh}
                        print shell completion script
  --version             show program's version number and exit
  -v, --verbose         list files that will be deleted
  --trash-dir TRASH_DIR
                        specify the trash directory to use
  --all-users           empty all trashcan of all the users
  -i, --interactive     ask before emptying trash directories
  -f                    don't ask before emptying trash directories
  --dry-run             show which files would have been removed

Report bugs to https://github.com/andreafrancia/trash-cli/issues
"""), '', 0]

    def test_h(self):
        result = run_command(self.tmp_dir, "trash-empty", ['-h'])

        assert [result.stdout[0:6],
                result.stderr,
                result.exit_code] == ["usage:", '', 0]

    def test_version(self):
        result = run_command(self.tmp_dir, "trash-empty", ['--version'])

        assert [result.stdout,
                result.stderr,
                result.exit_code] == ['trash-empty %s\n' % trash.version, '', 0]

    def test_on_invalid_option(self):
        result = run_command(self.tmp_dir, "trash-empty", ['--wrong-option'])

        assert [result.stdout,
                result.stderr.splitlines()[-1],
                result.exit_code] == [
                   '',
                   'trash-empty: error: unrecognized arguments: --wrong-option',
                   2]

    def test_on_print_time(self):
        result = run_command(self.tmp_dir, "trash-empty", ['--print-time'],
                             env={'TRASH_DATE': '1970-12-31T23:59:59'})

        assert result.all == ('1970-12-31T23:59:59\n', '', 0)

    def test_on_trash_date_not_parsable(self):
        result = run_command(self.tmp_dir, "trash-empty", ['--print-time'],
                             env={'TRASH_DATE': 'not a valid date'})

        assert ([result.stderr, result.exit_code] ==
                ['trash-empty: invalid TRASH_DATE: not a valid date\n', 0])
