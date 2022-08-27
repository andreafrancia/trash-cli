import datetime
import unittest

import pytest

from ..fake_trash_dir import FakeTrashDir
from ..support import MyPath
from ..run_command import normalize_options
from .. import run_command


@pytest.mark.slow
class TestEndToEndList(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.trash_dir = self.tmp_dir / 'trash-dir'
        self.fake_trash_dir = FakeTrashDir(self.trash_dir)

    def test_list(self):
        self.fake_trash_dir.add_trashinfo2("/file1", datetime.datetime(2000, 1, 1, 0, 0, 1))
        self.fake_trash_dir.add_trashinfo2("/file2", datetime.datetime(2000, 1, 1, 0, 0, 1))

        result = run_command.run_command(self.tmp_dir, "trash-list",
                                         ['--trash-dir', self.trash_dir])

        assert [
                   '2000-01-01 00:00:01 /file1',
                   '2000-01-01 00:00:01 /file2',
               ] == sorted(result.stdout.splitlines())

    def test_list_with_paths(self):
        self.fake_trash_dir.add_trashinfo3("base1", "/file1", datetime.datetime(2000, 1, 1, 0, 0, 1))
        self.fake_trash_dir.add_trashinfo3("base2", "/file2", datetime.datetime(2000, 1, 1, 0, 0, 1))

        result = run_command.run_command(self.tmp_dir, "trash-list",
                                         ['--trash-dir', self.trash_dir,
                                          '--files'])

        assert ('', [
            '2000-01-01 00:00:01 /file1 -> %s/files/base1' % self.trash_dir,
            '2000-01-01 00:00:01 /file2 -> %s/files/base2' % self.trash_dir,
        ]) == (result.stderr, sorted(result.stdout.splitlines()))

    def test_help(self):
        result = run_command.run_command(self.tmp_dir, "trash-list", ['--help'])

        self.assertEqual("""\
usage: trash-list [-h] [--version] [--volumes] [--trash-dirs]
                  [--trash-dir TRASH_DIRS] [--all-users]

List trashed files

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --volumes             list volumes
  --trash-dirs          list trash dirs
  --trash-dir TRASH_DIRS
                        specify the trash directory to use
  --all-users           list trashcans of all the users

Report bugs to https://github.com/andreafrancia/trash-cli/issues
""", normalize_options(result.stdout))

    def tearDown(self):
        self.tmp_dir.clean_up()
