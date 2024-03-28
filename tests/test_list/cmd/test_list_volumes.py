from tests.test_list.cmd.setup import Setup


class TestListVolumes(Setup):
    def test(self):
        self.user.volumes.append("/disk1")
        self.user.volumes.append("/disk2")
        self.user.volumes.append("/disk3")

        self.user.run_trash_list('--volumes')
        output = self.user.output()

        assert output == ('/disk1\n'
                          '/disk2\n'
                          '/disk3\n')
