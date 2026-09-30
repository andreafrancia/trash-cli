import datetime

from tests.support.dates import jan_11_2001
from tests.support.put.fake_fs.failing_fake_fs import FailOnMoveFakeFs
from tests.support.trash_dirs.given_trash import \
    GivenTrash
from tests.support.restore.restore_user import RestoreUser
from tests.test_restore.support.recording_logger import RecordingLogger

a_date = jan_11_2001()

class TestRestore2:
    def setup_method(self):
        self.fs = FailOnMoveFakeFs()
        self.trash = GivenTrash(self.fs)
        self.user = RestoreUser(
            environ={'XDG_DATA_HOME': '/data_home'},
            uid=1000,
            file_reader=self.fs,
            path_read_fs=self.fs,
            write_fs=self.fs,
            listing_fs=self.fs,
            version='1.2.3',
            volumes=self.fs,
            volume_path_fs=self.fs,
            top_trash_dir_rules_reader=self.fs,
            logger=RecordingLogger()
        )

    def test_should_print_version(self):
        res = self.cmd_run(['trash-restore', '--version'])

        assert 'trash-restore 1.2.3\n' == res.stdout

    def test_with_no_args_and_no_files_in_trashcan(self):
        res = self.cmd_run(['trash-restore'], from_dir='/cwd')

        assert ("No files trashed from current dir ('/cwd')\n" ==
                res.stdout)

    def test_restore_operation(self):
        self.trash.has_trashed_file('/cwd/parent/foo.txt', '/data_home/Trash',
                               datetime.datetime(2016, 1, 1), 'boo')
        assert '/cwd/parent/foo.txt' not in self.fs.find_all()
        assert '/data_home/Trash/info/foo.txt.trashinfo' in self.fs.find_all()
        assert '/data_home/Trash/files/foo.txt' in self.fs.find_all()

        res = self.cmd_run(['trash-restore'], reply='0', from_dir='/cwd')

        assert '' == res.stderr
        assert '/data_home/Trash/info/foo.txt.trashinfo' not in self.fs.find_all()
        assert '/data_home/Trash/files/foo.txt' not in self.fs.find_all()
        assert '/cwd/parent/foo.txt' in self.fs.find_all()

    def test_restore_operation_when_dest_exists(self):
        self.trash.has_trashed_file('/cwd/parent/foo.txt', '/data_home/Trash',
                               datetime.datetime(2016, 1, 1), 'boo')
        self.trash.has_file('/cwd/parent/foo.txt')
        assert '/cwd/parent/foo.txt' in self.fs.find_all()
        assert '/data_home/Trash/info/foo.txt.trashinfo' in self.fs.find_all()
        assert '/data_home/Trash/files/foo.txt' in self.fs.find_all()

        res = self.cmd_run(['trash-restore'], reply='0', from_dir='/cwd')

        assert res.stderr == 'Refusing to overwrite existing file "foo.txt".\n'
        assert '/cwd/parent/foo.txt' in self.fs.find_all()
        assert '/data_home/Trash/info/foo.txt.trashinfo' in self.fs.find_all()
        assert '/data_home/Trash/files/foo.txt' in self.fs.find_all()


    def test_when_user_reply_with_empty_string(self):
        self.trash.has_trashed_file('/cwd/parent/foo.txt', '/data_home/Trash',
                               datetime.datetime(2016, 1, 1), 'boo')

        res = self.cmd_run(['trash-restore'], reply='', from_dir='/cwd')

        assert res.last_line_of_stdout() == 'No files were restored'

    def test_batch_restore_continues_after_conflicts(self):
        self.trash.has_trashed_file('/cwd/a.txt', '/data_home/Trash', a_date, 'trash-a')
        self.trash.has_trashed_file('/cwd/b.txt', '/data_home/Trash', a_date, 'trash-b')
        self.trash.has_trashed_file('/cwd/c.txt', '/data_home/Trash', a_date, 'trash-c')
        self.trash.has_trashed_file('/cwd/d.txt', '/data_home/Trash', a_date, 'trash-d')
        self.trash.has_file('/cwd/b.txt', 'already-there-b')
        self.trash.has_file('/cwd/d.txt', 'already-there-d')

        res = self.cmd_run(['trash-restore', '--sort=path'],
                           reply='0-3', from_dir='/cwd')

        assert 1 == res.exit_code
        assert ('Refusing to overwrite existing file "b.txt".\n'
                'Refusing to overwrite existing file "d.txt".\n') == res.stderr
        assert 'trash-a' == self.fs.contents_of('/cwd/a.txt')
        assert 'trash-c' == self.fs.contents_of('/cwd/c.txt')
        assert 'already-there-b' == self.fs.contents_of('/cwd/b.txt')
        assert 'already-there-d' == self.fs.contents_of('/cwd/d.txt')
        assert ['b.txt.trashinfo', 'd.txt.trashinfo'] == self.fs.listdir('/data_home/Trash/info')

    def test_batch_restore_continues_after_move_error(self):
        self.trash.has_trashed_file('/cwd/a.txt', '/data_home/Trash', a_date, 'trash-a')
        self.trash.has_trashed_file('/cwd/b.txt', '/data_home/Trash', a_date, 'trash-b')
        self.fs.fail_move_on('/data_home/Trash/files/a.txt')

        res = self.cmd_run(['trash-restore', '--sort=path'],
                           reply='0,1', from_dir='/cwd')

        assert 1 == res.exit_code
        assert 'move failed\n' == res.stderr
        assert ['b.txt'] == self.fs.listdir('/cwd')
        assert ['a.txt.trashinfo'] == self.fs.listdir('/data_home/Trash/info')

    def test_when_user_reply_with_not_number(self):
        self.trash.has_trashed_file('/cwd/parent/foo.txt', '/data_home/Trash',
                               a_date, 'boo')

        res = self.cmd_run(['trash-restore'], reply='non numeric',
                           from_dir='/cwd')

        assert res.last_line_of_stderr() == \
               'Invalid entry: not an index: non numeric'
        assert 1 == res.exit_code

    def test_restore_refuses_to_overwrite_a_dangling_symlink(self):
        self.trash.has_trashed_file('/cwd/foo.txt', '/data_home/Trash',
                                    a_date, 'boo')
        self.fs.makedirs('/cwd', 0o755)
        self.fs.symlink('/nowhere', '/cwd/foo.txt')

        res = self.cmd_run(['trash-restore'], reply='0', from_dir='/cwd')

        assert res.stderr == 'Refusing to overwrite existing file "foo.txt".\n'
        assert self.fs.readlink('/cwd/foo.txt') == '/nowhere'
        assert self.fs.exists('/data_home/Trash/files/foo.txt')
        assert self.fs.exists('/data_home/Trash/info/foo.txt.trashinfo')

    def test_restore_refuses_to_overwrite_a_directory_even_with_overwrite(self):
        self.trash.has_trashed_file('/cwd/foo.txt', '/data_home/Trash',
                                    a_date, 'boo')
        self.fs.makedirs('/cwd/foo.txt', 0o755)

        res = self.cmd_run(['trash-restore', '--overwrite'], reply='0',
                           from_dir='/cwd')

        assert res.stderr == 'Refusing to overwrite existing file "foo.txt".\n'
        assert self.fs.listdir('/cwd/foo.txt') == []
        assert self.fs.exists('/data_home/Trash/files/foo.txt')

    def cmd_run(self, args, reply=None, from_dir=None):
        return self.user.run_restore(args, reply=reply, from_dir=from_dir)
