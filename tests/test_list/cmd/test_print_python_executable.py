import sys

from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.support.fs_fixture import real_fs_fixture
from tests.test_list.cmd.support.trash_list_user import trash_list_user

fs = real_fs_fixture
temp_dir = temp_dir_fixture
user = trash_list_user


class TestPrintPythonExecutable:
    def test(self, user):
        output = user.run_trash_list('--python')

        assert output.err_and_out() == ('', sys.executable + '\n')
