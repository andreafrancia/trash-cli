import pytest

from tests.support.run.run_command import run_command
from tests.support.fakes.fake_trash_dir import FakeTrashDir
from tests.support.fs_fixture import real_fs_fixture, fsx_fixture
from tests.support.trash_dirs.list_trash_dir import list_trash_dir
from tests.support.dirs.temp_dir import make_temp_dir, temp_dir_fixture


fs = real_fs_fixture
temp_dir = temp_dir_fixture
fsx = fsx_fixture


@pytest.mark.slow
class TestEmptyEndToEndWithTrashDir:
    @pytest.fixture(autouse=True)
    def setup_fs(self, fs, temp_dir, fsx):
        self.trash_dir = temp_dir / 'trash-dir'
        self.fake_trash_dir = FakeTrashDir(self.trash_dir, fs)

    def test_add_trashed_file(self):
        self.fake_trash_dir.add_trashed_file('foo', '/foo', 'FOO')

        assert list_trash_dir(self.trash_dir) == ['info/foo.trashinfo',
                                                  'files/foo']

    def test_trash_dir(self, temp_dir):
        self.fake_trash_dir.add_trashed_file('foo', '/foo', 'FOO')

        result = run_command(temp_dir,
                             "trash-empty", ['--trash-dir', self.trash_dir])

        assert [result.all, list_trash_dir(self.trash_dir)] == \
               [('', '', 0), []]

    def test_xdg_data_home(self, fs, temp_dir):
        xdg_data_home = temp_dir / 'xdg'
        custom_trash_dir = FakeTrashDir(xdg_data_home / 'Trash', fs)
        custom_trash_dir.add_trashed_file('foo', '/foo',
                                          'FOO')

        result = run_command(temp_dir, "trash-empty", [],
                             env={'XDG_DATA_HOME': xdg_data_home})

        trash_dir = xdg_data_home / 'Trash'
        assert [result.all, list_trash_dir(trash_dir)] == \
               [('', '', 0), []]

    def test_non_trash_info_is_not_deleted(
            self, fsx, temp_dir):
        fsx.make_file(self.trash_dir / 'info/non-trashinfo')

        result = run_command(temp_dir,
                             "trash-empty",
                             ['--trash-dir',
                              self.trash_dir])

        assert [result.all, list_trash_dir(self.trash_dir)] == \
               [('', '', 0), ['info/non-trashinfo']]

    def test_orphan_are_deleted(self, fs, fsx, temp_dir):
        fsx.make_file(self.trash_dir / 'files/orphan')
        fs.makedirs(self.trash_dir / 'files/orphan dir')

        result = run_command(temp_dir, "trash-empty",
                             ['--trash-dir', self.trash_dir])

        assert [result.all, list_trash_dir(self.trash_dir)] == \
               [('', '', 0), []]
