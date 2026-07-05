import unittest

import pytest

from tests.support.fakes.fake_trash_dir import FakeTrashDir
from tests.support.dirs.my_path import MyPath
from tests.support.run.run_command import run_command


@pytest.mark.slow
class TestOrphans(unittest.TestCase):
    def setUp(self):
        self.temp_dir = MyPath.make_temp_dir()
        self.trash_dir = self.temp_dir / 'trash-dir'
        self.fake_trash_dir = FakeTrashDir(self.trash_dir)

    def test_orphan_shown_normal_entry_suppressed(self):
        self.fake_trash_dir.add_trashinfo4("/file1", '2000-01-01 00:00:01')
        orphan_path = self.fake_trash_dir.add_orphan('orphan1')

        result = run_command(self.temp_dir, "trash-list",
                             ['--orphans', '--trash-dir',
                              self.trash_dir])

        assert result.stdout == orphan_path + '\n'
        assert result.stderr == ''

    def test_flag_absent_orphan_not_shown(self):
        self.fake_trash_dir.add_orphan('orphan1')

        result = run_command(self.temp_dir, "trash-list",
                             ['--trash-dir', self.trash_dir])

        assert 'orphan1' not in result.stdout

    def test_no_orphans_yields_empty_output(self):
        self.fake_trash_dir.add_trashinfo4("/file1", '2000-01-01 00:00:01')

        result = run_command(self.temp_dir, "trash-list",
                             ['--orphans', '--trash-dir',
                              self.trash_dir])

        assert result.stdout == ''
        assert result.exit_code == 0

    def test_multiple_orphans_all_listed(self):
        orphan1 = self.fake_trash_dir.add_orphan('orphan1')
        orphan2 = self.fake_trash_dir.add_orphan('orphan2')

        result = run_command(self.temp_dir, "trash-list",
                             ['--orphans', '--trash-dir',
                              self.trash_dir])

        assert set(result.stdout.splitlines()) == {orphan1, orphan2}

    def test_respects_trash_dir_selection(self):
        other_trash_dir = FakeTrashDir(self.temp_dir / 'other-trash-dir')
        orphan1 = self.fake_trash_dir.add_orphan('orphan1')
        other_trash_dir.add_orphan('orphan2')

        result = run_command(self.temp_dir, "trash-list",
                             ['--orphans', '--trash-dir',
                              self.trash_dir])

        assert result.stdout == orphan1 + '\n'

    def test_size_ignored_with_warning(self):
        orphan_path = self.fake_trash_dir.add_orphan('orphan1')

        result = run_command(self.temp_dir, "trash-list",
                             ['--orphans', '--size',
                              '--trash-dir', self.trash_dir])

        assert result.stderr == (
            "trash-list: --size is ignored when --orphans is used\n")
        assert result.stdout == orphan_path + '\n'

    def test_files_ignored_with_warning(self):
        orphan_path = self.fake_trash_dir.add_orphan('orphan1')

        result = run_command(self.temp_dir, "trash-list",
                             ['--orphans', '--files',
                              '--trash-dir', self.trash_dir])

        assert result.stderr == (
            "trash-list: --files is ignored when --orphans is used\n")
        assert result.stdout == orphan_path + '\n'

    def test_files_and_size_ignored_with_warning_alphabetical(self):
        orphan_path = self.fake_trash_dir.add_orphan('orphan1')

        result = run_command(self.temp_dir, "trash-list",
                             ['--orphans', '--files', '--size',
                              '--trash-dir', self.trash_dir])

        assert result.stderr == (
            "trash-list: --files and --size are ignored when "
            "--orphans is used\n")
        assert result.stdout == orphan_path + '\n'

    def test_files_and_size_warning_independent_of_argv_order(self):
        orphan_path = self.fake_trash_dir.add_orphan('orphan1')

        result = run_command(self.temp_dir, "trash-list",
                             ['--orphans', '--size', '--files',
                              '--trash-dir', self.trash_dir])

        assert result.stderr == (
            "trash-list: --files and --size are ignored when "
            "--orphans is used\n")
        assert result.stdout == orphan_path + '\n'

    def tearDown(self):
        self.temp_dir.clean_up()
