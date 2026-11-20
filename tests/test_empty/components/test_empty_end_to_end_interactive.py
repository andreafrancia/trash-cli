import datetime

import pytest

from tests.support.dirs.my_path import MyPath
from tests.support.fakes.fake_trash_dir import FakeTrashDir
from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.support.fs_fixture import real_fs_fixture
from tests.support.run.run_command import run_command
from trashcli.fslib.protocols.fs import Fs

fs = real_fs_fixture
temp_dir = temp_dir_fixture


@pytest.mark.slow
class TestEmptyEndToEndInteractive:
    @pytest.fixture(autouse=True)
    def setUp(self,
              fs,  # type: Fs
              temp_dir,  # type: MyPath
              ):
        self.tmp_dir = temp_dir
        self.xdg_data_home = self.tmp_dir / 'XDG_DATA_HOME'
        self.environ = {
            'XDG_DATA_HOME': self.xdg_data_home,
            'TRASH_VOLUMES': ':'
        }
        self.trash_dir = self.xdg_data_home / 'Trash'
        self.fake_trash_dir = FakeTrashDir(self.trash_dir, fs)

    def user_run_trash_empty(self, args):
        return run_command(self.tmp_dir, "trash-empty", args,
                           env=self.environ, input='y')

    def set_clock_at(self, yyyy_mm_dd):
        self.environ['TRASH_DATE'] = '%sT00:00:00' % yyyy_mm_dd

    def test_it_should_keep_files_newer_than_N_days(self):
        self.fake_trash_dir.add_trashinfo_with_date('foo',
                                                    datetime.date(2000, 1, 1))
        self.set_clock_at('2000-01-01')

        result = self.user_run_trash_empty(['-i'])

        assert result.all == (
            'Would empty the following trash directories:\n'
            '    - %s\n'
            'Proceed? (y/N) ' % self.trash_dir, '', 0)
