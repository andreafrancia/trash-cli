import os

import pytest

from tests.support.empty.empty_user import empty_user_fixture, EmptyUser
from tests.support.fs_fixture import real_fs_fixture
from tests.support.unreadable import unreadable_fixture
from tests.support.dirs.temp_dir import make_temp_dir, temp_dir_fixture_fs

temp_dir = temp_dir_fixture_fs
unreadable = unreadable_fixture
user = empty_user_fixture
fs = real_fs_fixture


@pytest.mark.slow
class TestEmptyCanRemovesReadonlyDir:
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
                                                             # type: EmptyUser
                                                             fs,
                                                             temp_dir):
        target = temp_dir / 'xdg_data_home/Trash/files' / 'proj'
        fs.makedirs(target / 'sub', 0o755)
        fs.write_file(target / 'sub' / 'f', 'x')
        fs.chmod(target / 'sub', 0o500)
        fs.chmod(target, 0o500)

        user.run_empty(environ={'XDG_DATA_HOME': temp_dir / 'xdg_data_home'})

        assert not fs.path_exists(target)
        assert user.stderr == ""
