import pytest

from tests.support.dirs.my_path import MyPath
from tests.support.fakes.fake_trash_dir import FakeTrashDir
from tests.support.dirs.temp_dir import temp_dir_fixture_fs
from tests.support.fs_fixture import real_fs_fixture
from tests.support.rm.rm_user import rm_user_fixture, RmUser

fs = real_fs_fixture
temp_dir = temp_dir_fixture_fs
user = rm_user_fixture


@pytest.mark.slow
class TestTrashRmRealFs:
    @pytest.fixture(autouse=True)
    def setup_user(self, user,
                   temp_dir):  # type: (RmUser, MyPath) -> None
        self.xdg_data_home = temp_dir / 'xdg'
        user.add_environ('XDG_DATA_HOME', self.xdg_data_home)
        self.trash = FakeTrashDir(self.xdg_data_home / 'Trash')

    def test_issue69(self, user):
        self.trash.add_trashinfo_without_path('foo')

        user.run_rm(['ignored'])

        assert (user.stderr ==
                "trash-rm: %s/Trash/info/foo.trashinfo: unable to parse 'Path'"
                '\n' % self.xdg_data_home)

    def test_integration(self, user, temp_dir):
        self.trash.add_trashinfo_basename_path("del", 'to/be/deleted')
        self.trash.add_trashinfo_basename_path("keep", 'to/be/kept')

        user.run_rm(['delete*'])

        assert self.trash.ls_info() == ['keep.trashinfo']
