import datetime

from tests.test_restore.support.fake_restore_fs import FakeRestoreFs
from tests.test_restore.support.restore_user import RestoreUser


class TestSearcher:
    def setup_method(self):
        self.fs = FakeRestoreFs()
        self.user = RestoreUser(environ={'HOME': '/home/user'},
                                uid=123,
                                file_reader=self.fs,
                                read_fs=self.fs,
                                write_fs=self.fs,
                                listing_file_system=self.fs,
                                version='1.0',
                                volumes=self.fs)


    def test_no_files_in_current_dir(self):
        self.fs.add_volume('/disk1')
        self.fs.add_file('/disk1/.Trash-123/info/not_a_trashinfo')
        self.fs.add_trash_file("/foo", '/home/user/.local/share/Trash',
                               datetime.datetime(2018, 1, 1, 0, 0), '')
        self.fs.add_trash_file("/disk1/bar", '/disk1/.Trash-123',
                               datetime.datetime(2018, 1, 1, 0, 0), '')

        res = self.run_restore([], from_dir='/home/user')

        assert (res.output() ==
                "No files trashed from current dir ('/home/user')\n")

    def test_file_in_cur_dir(self):
        self.fs.add_trash_file("/home/user/foo", '/home/user/.local/share/Trash',
                               datetime.datetime(2018, 1, 1, 0, 0), '')

        res = self.run_restore([], from_dir='/home/user')

        assert (res.output() ==
                '   0 2018-01-01 00:00:00 /home/user/foo\n'
                'Exiting\n')

    def test_actual_restore(self):
        self.fs.add_trash_file("/home/user/foo", '/home/user/.local/share/Trash',
                               datetime.datetime(2018, 1, 1, 0, 0),
                           "contents of foo\n")
        assert not self.fs.path_exists('/home/user/foo')

        res = self.run_restore([], reply="0", from_dir='/home/user')

        assert (res.output() ==
                '   0 2018-01-01 00:00:00 /home/user/foo\n')
        assert (self.fs.contents_of('/home/user/foo') == "contents of foo\n")

    def run_restore(self, args, reply='', from_dir=None):
        return self.user.run_restore(args, reply, from_dir)
