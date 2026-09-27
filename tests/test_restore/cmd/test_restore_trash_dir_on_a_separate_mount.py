import datetime

from tests.support.restore.fake_restore_fs import FakePathFs
from tests.support.restore.restore_user import RestoreUser
from tests.test_restore.support.capture_logger import CaptureLogger


# Regression tests for issues #419 and #420: trash-put always writes absolute
# Path= entries in the home trash (and in any trash dir that is not a volume
# trash), but trash-restore refused them with "Path= must be relative for
# volume trashes" whenever that trash dir did not live on the '/' mount point,
# e.g. when /home (#420) or /tmp (#419) is a separate mount.
# Only the volume trashes ($topdir/.Trash/$uid and $topdir/.Trash-$uid) must
# contain relative paths.
class TestRestoreTrashDirOnASeparateMount:
    def setup_method(self):
        self.fs = FakePathFs()
        self.logger = CaptureLogger()
        self.user = RestoreUser(environ={'HOME': '/home/user'},
                                uid=123,
                                file_reader=self.fs,
                                path_read_fs=self.fs,
                                write_fs=self.fs,
                                listing_fs=self.fs,
                                version='1.0',
                                volumes=self.fs,
                                volume_path_fs=self.fs,
                                logger=self.logger)

    # Issue #420: /home is a separate mount point.
    def test_home_trash_on_a_separate_mount_is_restorable(self):
        self.fs.add_volume('/home')
        trashed_file = self.fs.make_trashed_file('/home/user/foo',
                                                 '/home/user/.local/share/Trash',
                                                 date_at(2018, 1, 1),
                                                 'contents of foo')

        res = self.user.run_restore([], reply='0', from_dir='/home/user')

        assert (res.output(), self.logger.captured) == (
            '   0 2018-01-01 00:00:00 /home/user/foo\n', [])
        assert self.fs.contents_of('/home/user/foo') == 'contents of foo'
        assert not self.fs.exists(trashed_file.info_file)

    # Issue #419: the test suite uses --trash-dir with a trash dir created in
    # a temp dir under /tmp, and /tmp is a separate mount point (tmpfs).
    def test_trash_dir_from_cli_on_a_separate_mount_is_restorable(self):
        self.fs.add_volume('/tmp')
        self.fs.make_trashed_file('/cwd/foo', '/tmp/xyz/trash-dir',
                                  date_at(2018, 1, 1), '')

        res = self.user.run_restore(['trash-restore', '--trash-dir',
                                     '/tmp/xyz/trash-dir', '/'],
                                    from_dir='/cwd')

        assert (res.output(), self.logger.captured) == (
            '   0 2018-01-01 00:00:00 /cwd/foo\n'
            'No files were restored\n', [])

    # The fix must not weaken the check for the real volume trashes, also
    # when they are passed with --trash-dir.
    def test_volume_trash_from_cli_still_refuses_absolute_paths(self):
        self.fs.add_volume('/tmp')
        self.fs.make_trashed_file('/etc/passwd', '/tmp/.Trash-123',
                                  date_at(2018, 1, 1), '')

        res = self.user.run_restore(['trash-restore', '--trash-dir',
                                     '/tmp/.Trash-123', '/'],
                                    from_dir='/cwd')

        assert (res.output(), self.logger.captured) == (
            "No files trashed from current dir ('/cwd')\n",
            ['WARN: Non parsable trashinfo file: '
             '/tmp/.Trash-123/info/passwd.trashinfo, '
             'because Path= must be relative for volume trashes'])

    def test_shared_volume_trash_still_refuses_absolute_paths(self):
        self.fs.add_volume('/tmp')
        self.fs.make_trashed_file('/etc/passwd', '/tmp/.Trash/123',
                                  date_at(2018, 1, 1), '')

        res = self.user.run_restore(['trash-restore', '--trash-dir',
                                     '/tmp/.Trash/123', '/'],
                                    from_dir='/cwd')

        assert (res.output(), self.logger.captured) == (
            "No files trashed from current dir ('/cwd')\n",
            ['WARN: Non parsable trashinfo file: '
             '/tmp/.Trash/123/info/passwd.trashinfo, '
             'because Path= must be relative for volume trashes'])


def date_at(year, month, day):
    return datetime.datetime(year, month, day, 0, 0)
