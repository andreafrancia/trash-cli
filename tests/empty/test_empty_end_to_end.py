import os
import unittest

from trashcli import trash
from .. import run_command
from ..fake_trash_dir import FakeTrashDir
from ..support import MyPath


class TestEmptyEndToEnd(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()

    def test_help(self):
        result = run_command.run_command(self.tmp_dir, "trash-empty",
                                         ['--help'])
        self.assertEqual(["""\
Usage: trash-empty [days]

Purge trashed files.

Options:
  --version   show program's version number and exit
  -h, --help  show this help message and exit

Report bugs to https://github.com/andreafrancia/trash-cli/issues
""", '', 0],
                         [result.stdout,
                          result.stderr,
                          result.exit_code])

    def test_h(self):
        result = run_command.run_command(self.tmp_dir, "trash-empty",
                                         ['-h'])
        self.assertEqual(["""\
Usage: trash-empty [days]

Purge trashed files.

Options:
  --version   show program's version number and exit
  -h, --help  show this help message and exit

Report bugs to https://github.com/andreafrancia/trash-cli/issues
""", '', 0],
                         [result.stdout,
                          result.stderr,
                          result.exit_code])

    def test_version(self):
        result = run_command.run_command(self.tmp_dir, "trash-empty",
                                         ['--version'])
        self.assertEqual(['trash-empty %s\n' % trash.version, '', 0],
                         [result.stdout,
                          result.stderr,
                          result.exit_code])

    def tearDown(self):
        self.tmp_dir.clean_up()


class TestEmptyEndToEndWithTrashDir(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.trash_dir = self.tmp_dir / 'trash-dir'
        self.fake_trash_dir = FakeTrashDir(self.trash_dir)

    def test_add_trashed_file(self):
        self.fake_trash_dir.add_trashed_file('foo', '/foo', 'FOO')

        assert self.list_trash() == ['foo.trashinfo', 'foo']

    def test_trash_dir(self):
        self.fake_trash_dir.add_trashed_file('foo', '/foo', 'FOO')

        result = run_command.run_command(self.tmp_dir, "trash-empty",
                                         ['--trash-dir', self.trash_dir])

        assert [result.all, self.list_trash()] == \
               [['', '', 0], []]

    def list_trash(self):
        return os.listdir(self.trash_dir / 'info') + \
               os.listdir(self.trash_dir / 'files')

    def tearDown(self):
        self.tmp_dir.clean_up()
