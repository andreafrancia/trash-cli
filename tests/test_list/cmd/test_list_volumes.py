from tests.support.my_path import MyPath
from tests.test_list.cmd.support.trash_list_user import TrashListUser


class TestListVolumes:
    def setup_method(self):
        self.user = TrashListUser(MyPath.make_temp_dir())

    def test(self):
        self.user.volumes.append("/disk1")
        self.user.volumes.append("/disk2")
        self.user.volumes.append("/disk3")

        output = self.user.run_trash_list('--volumes')

        assert output.whole_output() == ('/disk1\n'
                                         '/disk2\n'
                                         '/disk3\n')
