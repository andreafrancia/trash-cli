import os

import pytest

from tests.support.dirs.temp_dir import make_temp_dir, temp_dir_fixture_fs
from tests.support.fakes.fake_trash_dir import FakeTrashDir
from tests.support.fs_fixture import real_fs_fixture
from tests.support.rm.rm_user import rm_user_fixture

fs = real_fs_fixture
user = rm_user_fixture


@pytest.mark.slow
class TestTrashRmCanRemoveReadonlyDir:
    @pytest.fixture
    def temp_dir(self, fs):
        temp_dir = make_temp_dir(fs)
        yield temp_dir
        # restore write bits so a failed run can still be cleaned up
        for root, dirs, files in fs.walk_no_follow(temp_dir):
            for name in dirs:
                fs.chmod(os.path.join(root, name), 0o700)
        temp_dir.clean_up()

    def test_a_directory_without_write_permission_is_removed(self,
                                                              user,
                                                              fs,
                                                              temp_dir):
        xdg_data_home = temp_dir / 'xdg_data_home'
        fake_trash_dir = FakeTrashDir(xdg_data_home / 'Trash')
        target = xdg_data_home / 'Trash/files' / 'proj'
        fs.makedirs(target / 'sub', 0o755)
        fs.write_file(target / 'sub' / 'f', 'x')
        fs.chmod(target / 'sub', 0o500)
        fs.chmod(target, 0o500)
        fake_trash_dir.add_trashinfo_basename_path('proj', '/original/proj')
        user.add_environ('HOME', temp_dir)
        user.add_environ('XDG_DATA_HOME', xdg_data_home)

        user.run_rm(['proj'])

        assert not fs.path_exists(target)
        assert fake_trash_dir.ls_info() == []
        assert user.stderr == ""
