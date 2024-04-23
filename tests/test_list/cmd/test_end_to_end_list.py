import datetime
import unittest

import pytest

from tests.support import run_command
from tests.support.fake_trash_dir import FakeTrashDir
from tests.support.help_reformatting import reformat_help_message
from tests.support.my_path import MyPath


@pytest.mark.slow
class TestEndToEndList(unittest.TestCase):
    def setUp(self):
        self.temp_dir = MyPath.make_temp_dir()
        self.trash_dir = self.temp_dir / 'trash-dir'
        self.fake_trash_dir = FakeTrashDir(self.trash_dir)

    def test_list(self):
        self.fake_trash_dir.add_trashinfo4("/file1", '2000-01-01 00:00:01')
        self.fake_trash_dir.add_trashinfo4("/file2", '2000-01-01 00:00:02')

        result = run_command.run_command(self.temp_dir, "trash-list",
                                         ['--trash-dir', self.trash_dir])

        assert result.all_lines() == {'2000-01-01 00:00:01 /file1',
                                      '2000-01-01 00:00:02 /file2', }

    def test_list_trash_dirs(self):
        result = run_command.run_command(
            self.temp_dir, "trash-list",
            ['--trash-dirs', '--trash-dir=/home/user/.local/share/Trash'])
        assert result.all == ('/home/user/.local/share/Trash\n', '', 0)

    def test_list_with_paths(self):
        self.fake_trash_dir.add_trashinfo3("base1", "/file1",
                                           datetime.datetime(2000, 1, 1, 0, 0,
                                                             1))
        self.fake_trash_dir.add_trashinfo3("base2", "/file2",
                                           datetime.datetime(2000, 1, 1, 0, 0,
                                                             1))

        result = run_command.run_command(self.temp_dir, "trash-list",
                                         ['--trash-dir', self.trash_dir,
                                          '--files'])

        assert ('', [
            '2000-01-01 00:00:01 /file1 -> %s/files/base1' % self.trash_dir,
            '2000-01-01 00:00:01 /file2 -> %s/files/base2' % self.trash_dir,
        ]) == (result.stderr, sorted(result.stdout.splitlines()))

    def test_help(self):
        result = run_command.run_command(self.temp_dir, "trash-list",
                                         ['--help'])

        self.assertEqual(reformat_help_message("""\
usage: trash-list [-h] [--print-completion {bash,zsh,tcsh}] [--version]
                  [--volumes] [--trash-dirs] [--trash-dir TRASH_DIRS]
                  [--all-users]

List trashed files

options:
  -h, --help            show this help message and exit
  --print-completion {bash,zsh,tcsh}
                        print shell completion script
  --version             show program's version number and exit
  --volumes             list volumes
  --trash-dirs          list trash dirs
  --trash-dir TRASH_DIRS
                        specify the trash directory to use
  --all-users           list trashcans of all the users

Report bugs to https://github.com/andreafrancia/trash-cli/issues
"""), result.stderr + result.reformatted_help())

    def tearDown(self):
        self.temp_dir.clean_up()
