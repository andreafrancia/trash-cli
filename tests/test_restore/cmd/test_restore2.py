import datetime
import unittest

from tests.support.py2mock import Mock, call

from tests.support.restore.fake_restore_fs import FakeRestoreFs
from tests.support.restore.restore_user import RestoreUser
from trashcli.restore.file_system import RestoreWriteFileSystem


class TestRestore2(unittest.TestCase):
    def setUp(self):
        self.write_fs = Mock(spec=RestoreWriteFileSystem)
        self.fs = FakeRestoreFs()
        self.user = RestoreUser(
            environ={'XDG_DATA_HOME': '/data_home'},
            uid=1000,
            file_reader=self.fs,
            read_fs=self.fs,
            write_fs=self.write_fs,
            listing_file_system=self.fs,
            version='1.2.3',
            volumes=self.fs,
        )

    def test_should_print_version(self):
        res = self.cmd_run(['trash-restore', '--version'])

        assert 'trash-restore 1.2.3\n' == res.stdout

    def test_with_no_args_and_no_files_in_trashcan(self):
        res = self.cmd_run(['trash-restore'], from_dir='cwd')

        assert ("No files trashed from current dir ('cwd')\n" ==
                res.stdout)

    def test_restore_operation(self):
        self.fs.add_trash_file('/cwd/parent/foo.txt', '/data_home/Trash',
                               datetime.datetime(2016, 1, 1), 'boo')

        res = self.cmd_run(['trash-restore'], reply='0', from_dir='/cwd')

        assert '' == res.stderr
        assert ([call.mkdirs('/cwd/parent'),
                 call.move('/data_home/Trash/files/foo.txt',
                           '/cwd/parent/foo.txt'),
                 call.remove_file('/data_home/Trash/info/foo.txt.trashinfo')]
                == self.write_fs.mock_calls)

    def test_restore_operation_when_dest_exists(self):
        self.fs.add_trash_file('/cwd/parent/foo.txt', '/data_home/Trash',
                               datetime.datetime(2016, 1, 1), 'boo')
        self.fs.add_file('/cwd/parent/foo.txt')

        res = self.cmd_run(['trash-restore'], reply='0', from_dir='/cwd')

        assert 'Refusing to overwrite existing file "foo.txt".\n' == res.stderr
        assert ([] == self.write_fs.mock_calls)

    def test_when_user_reply_with_empty_string(self):
        self.fs.add_trash_file('/cwd/parent/foo.txt', '/data_home/Trash',
                               datetime.datetime(2016, 1, 1), 'boo')

        res = self.cmd_run(['trash-restore'], reply='', from_dir='/cwd')

        assert res.last_line_of_stdout() == 'No files were restored'

    def test_when_user_reply_with_not_number(self):
        self.fs.add_trash_file('/cwd/parent/foo.txt', '/data_home/Trash',
                               datetime.datetime(2016, 1, 1), 'boo')

        res = self.cmd_run(['trash-restore'], reply='non numeric', from_dir='/cwd')

        assert res.last_line_of_stderr() == \
               'Invalid entry: not an index: non numeric'
        assert 1 == res.exit_code

    def cmd_run(self, args, reply=None, from_dir=None):
        return self.user.run_restore(args, reply=reply, from_dir=from_dir)
