import datetime
import unittest

import pytest

from ..support import run_command
from tests.support.fake_trash_dir import FakeTrashDir
from ..support.my_path import MyPath


@pytest.mark.slow
class TestEmptyEndToEndInteractive(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.xdg_data_home = self.tmp_dir / 'XDG_DATA_HOME'
        self.environ = {
            'XDG_DATA_HOME': self.xdg_data_home,
            'TRASH_VOLUMES': ':'
        }
        self.trash_dir = self.xdg_data_home / 'Trash'
        self.fake_trash_dir = FakeTrashDir(self.trash_dir)

    def user_run_trash_empty(self, args):
        return run_command.run_command(self.tmp_dir,
                                       "trash-empty",
                                       args,
                                       env=self.environ,
                                       input='y')

    def set_clock_at(self, yyyy_mm_dd):
        self.environ['TRASH_DATE'] = '%sT00:00:00' % yyyy_mm_dd

    def test_it_should_keep_files_newer_than_N_days(self):
        self.fake_trash_dir.add_trashinfo_with_date('foo', datetime.date(2000, 1, 1))
        self.set_clock_at('2000-01-01')

        result = self.user_run_trash_empty(['-i'])

        assert result.all == [
            'Would empty the following trash directories:\n'
            '    - %s\n'
            'Proceed? (y/N) ' % self.trash_dir, '', 0]

    def tearDown(self):
        self.tmp_dir.clean_up()
