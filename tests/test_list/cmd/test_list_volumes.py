from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.support.fs_fixture import real_fs_fixture
from tests.test_list.cmd.support.trash_list_user import trash_list_user

fs = real_fs_fixture
user = trash_list_user
temp_dir = temp_dir_fixture


class TestListVolumes:

    def test(self, user):
        user.add_disk("/disk1")
        user.add_disk("/disk2")
        user.add_disk("/disk3")

        output = user.run_trash_list('--volumes')

        assert output.whole_output() == ('/disk1\n'
                                         '/disk2\n'
                                         '/disk3\n')
