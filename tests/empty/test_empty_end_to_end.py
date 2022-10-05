import unittest

from trashcli import trash

from .. import run_command
from ..run_command import normalize_options
from ..support.my_path import MyPath


class TestEmptyEndToEnd(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()

    def test_help(self):
        result = run_command.run_command(self.tmp_dir, "trash-empty",
                                         ['--help'])
        self.assertEqual(["""\
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
""", '', 0],
                         [normalize_options(result.stdout),
                          result.stderr,
                          result.exit_code])

    def test_h(self):
        result = run_command.run_command(self.tmp_dir, "trash-empty",
                                         ['-h'])
        self.assertEqual(["usage:", '', 0],
                         [result.stdout[0:6],
                          result.stderr,
                          result.exit_code])

    def test_version(self):
        result = run_command.run_command(self.tmp_dir, "trash-empty",
                                         ['--version'])
        self.assertEqual(['trash-empty %s\n' % trash.version, '', 0],
                         [result.stdout,
                          result.stderr,
                          result.exit_code])

    def test_on_invalid_option(self):
        result = run_command.run_command(self.tmp_dir, "trash-empty",
                                         ['--wrong-option'])

        self.assertEqual(['',
                          'trash-empty: error: unrecognized arguments: --wrong-option',
                          2],
                         [result.stdout,
                          result.stderr.splitlines()[-1],
                          result.exit_code])

    def test_on_print_time(self):
        result = run_command.run_command(
            self.tmp_dir, "trash-empty",
            ['--print-time'],
            env={'TRASH_DATE': '1970-12-31T23:59:59'})

        self.assertEqual(['1970-12-31T23:59:59\n',
                          '',
                          0],
                         result.all)

    def test_on_trash_date_not_parsable(self):
        result = run_command.run_command(
            self.tmp_dir, "trash-empty",
            ['--print-time'],
            env={'TRASH_DATE': 'not a valid date'})

        self.assertEqual(['trash-empty: invalid TRASH_DATE: not a valid date\n',
                          0],
                         [result.stderr, result.exit_code])

    def tearDown(self):
        self.tmp_dir.clean_up()
