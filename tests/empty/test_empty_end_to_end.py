import os
import unittest

from trashcli import trash
from .. import run_command
from ..fake_trash_dir import FakeTrashDir
from ..files import make_file
from ..support import MyPath, list_trash_dir


class TestEmptyEndToEnd(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()

    def test_help(self):
        result = run_command.run_command(self.tmp_dir, "trash-empty",
                                         ['--help'])
        self.assertEqual(["""\
usage: trash-empty [-h] [--version] [--trash-dir TRASH_DIR] [--all-users] [-i]
                   [days]

Purge trashed files.

positional arguments:
  days

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --trash-dir TRASH_DIR
                        specify the trash directory to use
  --all-users           empty all trashcan of all the users
  -i, --interactive     ask before emptying trash directories

Report bugs to https://github.com/andreafrancia/trash-cli/issues
""", '', 0],
                         [result.stdout,
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


class TestEmptyEndToEndWithTrashDir(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.trash_dir = self.tmp_dir / 'trash-dir'
        self.fake_trash_dir = FakeTrashDir(self.trash_dir)

    def test_add_trashed_file(self):
        self.fake_trash_dir.add_trashed_file('foo', '/foo', 'FOO')

        assert list_trash_dir(self.trash_dir) == ['info/foo.trashinfo',
                                                  'files/foo']

    def test_trash_dir(self):
        self.fake_trash_dir.add_trashed_file('foo', '/foo', 'FOO')

        result = run_command.run_command(self.tmp_dir, "trash-empty",
                                         ['--trash-dir', self.trash_dir])

        assert [result.all, list_trash_dir(self.trash_dir)] == \
               [['', '', 0], []]

    def test_xdg_data_home(self):
        xdg_data_home = self.tmp_dir / 'xdg'
        FakeTrashDir(xdg_data_home / 'Trash').add_trashed_file('foo', '/foo', 'FOO')

        result = run_command.run_command(self.tmp_dir, "trash-empty",
                                         [], env={'XDG_DATA_HOME': xdg_data_home})

        trash_dir = xdg_data_home / 'Trash'
        assert [result.all, list_trash_dir(trash_dir)] == \
               [['', '', 0], []]

    def test_non_trash_info_is_not_deleted(self):
        make_file(self.trash_dir / 'info' / 'non-trashinfo')

        result = run_command.run_command(self.tmp_dir, "trash-empty",
                                         ['--trash-dir', self.trash_dir])

        assert [result.all, list_trash_dir(self.trash_dir)] == \
               [['', '', 0], ['info/non-trashinfo']]

    def test_orphan_are_deleted(self):
        make_file(self.trash_dir / 'files' / 'orphan')
        os.makedirs(self.trash_dir / 'files' / 'orphan dir')

        result = run_command.run_command(self.tmp_dir, "trash-empty",
                                         ['--trash-dir', self.trash_dir])

        assert [result.all, list_trash_dir(self.trash_dir)] == \
               [['', '', 0], []]

    def tearDown(self):
        self.tmp_dir.clean_up()
