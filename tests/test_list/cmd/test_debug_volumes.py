from tests.test_list.cmd.support.trash_list_user import trash_list_user  # noqa

user = trash_list_user


class TestDebugVolumes:
    def test_prints_physical_and_virtual_partitions_and_df_output(self, user):
        user.fake_disk_partitions.add_physical('/dev/sdb1', '/mnt', 'ext4')
        user.fake_disk_partitions.add_physical('/dev/sda1', '/', 'ext4')
        user.fake_disk_partitions.add_virtual('tmpfs', '/tmp', 'tmpfs')
        user.fake_disk_partitions.add_virtual('proc', '/proc', 'proc')
        user.fake_df.set_output('df output\n')

        output = user.run_trash_list('--debug-volumes')

        assert output.err_and_out() == ('', (
            "physical ->\n"
            "[FakePartition(device='/dev/sda1', mountpoint='/', fstype='ext4'),\n"
            " FakePartition(device='/dev/sdb1', mountpoint='/mnt', fstype='ext4')]\n"
            "virtual ->\n"
            "[FakePartition(device='proc', mountpoint='/proc', fstype='proc'),\n"
            " FakePartition(device='tmpfs', mountpoint='/tmp', fstype='tmpfs')]\n"
            "df output\n"))

    def test_when_there_are_no_partitions(self, user):
        output = user.run_trash_list('--debug-volumes')

        assert output.err_and_out() == ('', "physical ->\n"
                                            "[]\n"
                                            "virtual ->\n"
                                            "[]\n")
