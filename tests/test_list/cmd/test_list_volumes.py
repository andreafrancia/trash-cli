from tests.test_list.cmd.support.trash_list_user import trash_list_user  # noqa

user = trash_list_user


class TestListVolumes:

    def test(self, user):
        user.add_disk("/disk1")
        user.add_disk("/disk2")
        user.add_disk("/disk3")

        output = user.run_trash_list('--volumes')

        assert output.whole_output() == ('/disk1\n'
                                         '/disk2\n'
                                         '/disk3\n')
