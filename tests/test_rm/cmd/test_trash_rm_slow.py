import pytest

from tests.support.fakes.fake_trash_dir import FakeTrashDir
from tests.support.dirs.temp_dir import temp_dir_fixture_fs
from tests.support.fs_fixture import real_fs_fixture
from tests.support.rm.rm_user import rm_user_fixture

fs = real_fs_fixture
temp_dir = temp_dir_fixture_fs
user = rm_user_fixture


@pytest.mark.slow
class TestTrashRm:
    @pytest.fixture(autouse=True)
    def fake_trash_dir(self, xdg_data_home):
        return FakeTrashDir(xdg_data_home / 'Trash')

    @pytest.fixture
    def xdg_data_home(self, temp_dir):
        return temp_dir

    def test_issue69(self, user, xdg_data_home, fake_trash_dir):
        fake_trash_dir.add_trashinfo_without_path('foo')

        user.run_rm(['ignored'])

        assert (user.stderr ==
                "trash-rm: %s/Trash/info/foo.trashinfo: unable to parse 'Path'"
                '\n' % xdg_data_home)

    def test_integration(self, user, fake_trash_dir):
        fake_trash_dir.add_trashinfo_basename_path("del", 'to/be/deleted')
        fake_trash_dir.add_trashinfo_basename_path("keep", 'to/be/kept')

        user.run_rm(['delete*'])

        assert fake_trash_dir.ls_info() == ['keep.trashinfo']
