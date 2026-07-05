import unittest

import pytest

from tests.support.fakes.fake_trash_dir import FakeTrashDir
from tests.support.dirs.my_path import MyPath
from tests.support.run.run_command import run_command


@pytest.mark.slow
class TestShowNonTrashinfo(unittest.TestCase):
    def setUp(self):
        self.temp_dir = MyPath.make_temp_dir()
        self.trash_dir = self.temp_dir / 'trash-dir'
        self.fake_trash_dir = FakeTrashDir(self.trash_dir)

    def test_orphan_shown_normal_entry_suppressed(self):
        self.fake_trash_dir.add_trashinfo4("/file1", '2000-01-01 00:00:01')
        orphan_path = self.fake_trash_dir.add_orphan('orphan1')

        result = run_command(self.temp_dir, "trash-list",
                             ['--show-non-trashinfo', '--trash-dir',
                              self.trash_dir])

        assert result.stdout == orphan_path + '\n'
        assert result.stderr == ''

    def test_flag_absent_orphan_not_shown(self):
        self.fake_trash_dir.add_orphan('orphan1')

        result = run_command(self.temp_dir, "trash-list",
                             ['--trash-dir', self.trash_dir])

        assert 'orphan1' not in result.stdout

    def tearDown(self):
        self.temp_dir.clean_up()
