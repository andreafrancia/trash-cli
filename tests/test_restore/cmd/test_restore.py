import datetime

from tests.support.asserts.assert_that import assert_that
from tests.test_restore.support.fake_restore_fs import FakeRestoreFs
from tests.test_restore.support.has_been_restored_matcher import \
    has_been_restored, has_not_been_restored
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

    def test_will_not_detect_trashed_file_in_dirs_other_than_cur_dir(self):
        self.fs.add_volume('/disk1')
        self.fs.add_file('/disk1/.Trash-123/info/not_a_trashinfo')
        self.fs.add_trash_file("/foo", '/home/user/.local/share/Trash',
                               date_at(2018, 1, 1), '')
        self.fs.add_trash_file("/disk1/bar", '/disk1/.Trash-123',
                               date_at(2018, 1, 1), '')

        res = self.run_restore([], from_dir='/home/user')

        assert (res.output() ==
                "No files trashed from current dir ('/home/user')\n")

    def test_will_show_file_in_cur_dir(self):
        self.fs.add_trash_file("/home/user/foo",
                               '/home/user/.local/share/Trash',
                               date_at(2018, 1, 1), '')

        res = self.run_restore([], from_dir='/home/user')

        assert (res.output() ==
                '   0 2018-01-01 00:00:00 /home/user/foo\n'
                'No files were restored\n')

    def test_actual_restore(self):
        trashed_file = self.fs.make_trashed_file("/home/user/foo",
                                                 '/home/user/.local/share/Trash',
                                                 date_at(2018, 1, 1),
                                                 "contents of foo\n")
        assert_that(trashed_file, has_not_been_restored(self.fs))

        res = self.run_restore([], reply="0", from_dir='/home/user')

        assert (res.output() ==
                '   0 2018-01-01 00:00:00 /home/user/foo\n')
        assert_that(trashed_file, has_been_restored(self.fs))
        assert (self.fs.contents_of('/home/user/foo') == "contents of foo\n")

    def test_will_sort_by_date_by_default(self):
        self.add_file_trashed_at("/home/user/third", date_at(2013, 1, 1))
        self.add_file_trashed_at("/home/user/second", date_at(2012, 1, 1))
        self.add_file_trashed_at("/home/user/first", date_at(2011, 1, 1))

        res = self.run_restore([], from_dir='/home/user')

        assert (res.output() ==
                '   0 2011-01-01 00:00:00 /home/user/first\n'
                '   1 2012-01-01 00:00:00 /home/user/second\n'
                '   2 2013-01-01 00:00:00 /home/user/third\n'
                'No files were restored\n')

    def test_will_sort_by_path(self):
        self.add_file_trashed_at("/home/user/ccc", date_at(2011, 1, 1))
        self.add_file_trashed_at("/home/user/bbb", date_at(2011, 1, 1))
        self.add_file_trashed_at("/home/user/aaa", date_at(2011, 1, 1))

        res = self.run_restore(['trash-restore', '--sort=path'], from_dir='/home/user')

        assert (res.output() ==
                '   0 2011-01-01 00:00:00 /home/user/aaa\n'
                '   1 2011-01-01 00:00:00 /home/user/bbb\n'
                '   2 2011-01-01 00:00:00 /home/user/ccc\n'
                'No files were restored\n')

    def run_restore(self, args, reply='', from_dir=None):
        return self.user.run_restore(args, reply, from_dir)

    def add_file_trashed_at(self, original_location, deletion_date):
        self.fs.make_trashed_file(original_location, '/home/user/.local/share/Trash',
                                  deletion_date, '')


def date_at(year, month, day):
    return datetime.datetime(year, month, day, 0, 0)
