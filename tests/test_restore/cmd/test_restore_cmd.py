import datetime
from typing import List
from typing import Optional

from tests.support.put.fake_fs.fake_fs import FakeFs
from tests.support.restore.fs.fake_restore_fs import FakeRestoreFs
from tests.support.restore.restore_user import RestoreUser
from tests.support.run.cmd_result import CmdResult


class TestRestoreCmd:
    def setup_method(self):
        self.fs = FakeFs()
        self.restore_fs = FakeRestoreFs(self.fs)

    def test_add_trash_file(self):
        self.restore_fs.add_trash_file('/cwd/parent/foo.txt',
                                       '/data_home/Trash',
                                       datetime.datetime(2016, 1, 1),
                                       b'boo')

        assert join_checks(self.restore_fs.save_state().check_final_listing_is([
            '/data_home/',
            '/data_home/Trash/',
            '/data_home/Trash/files/',
            '/data_home/Trash/files/foo.txt: boo',
            '/data_home/Trash/info/',
            '/data_home/Trash/info/foo.txt.trashinfo: '
            '[Trash Info]\n'
            'Path=/cwd/parent/foo.txt\n'
            'DeletionDate=2016-01-01T00:00:00\n'])) == []

    def test_restore_operation(self):
        self.restore_fs.add_trash_file('/cwd/parent/foo.txt',
                                       '/data_home/Trash',
                                       datetime.datetime(2016, 1, 1),
                                       b'boo')
        state = self.restore_fs.save_state()

        result = self.cmd_run(['trash-restore'], reply='0',
                              cwd='/cwd')

        assert join_checks(
            result.check_stderr_is_empty(),
            state.check_directory_created('/cwd/parent'),
            state.check_file_moved('/data_home/Trash/files/foo.txt',
                                   '/cwd/parent/foo.txt'),
            state.check_file_removed('/data_home/Trash/info/foo.txt.trashinfo'),
            state.check_final_listing_is([
                '/cwd/',
                '/cwd/parent/',
                '/cwd/parent/foo.txt: boo',
                '/data_home/',
                '/data_home/Trash/',
                '/data_home/Trash/files/',
                '/data_home/Trash/info/',
            ]),
        ) == []

    def test_restore_operation_when_dest_exists(self):
        self.restore_fs.add_trash_file('/cwd/parent/foo.txt',
                                       '/data_home/Trash',
                                       datetime.datetime(2016, 1, 1),
                                       b'boo')
        self.restore_fs.add_file('/cwd/parent/foo.txt')
        state = self.restore_fs.save_state()

        result = self.cmd_run(['trash-restore'], reply='0', cwd='/cwd')

        assert 'Refusing to overwrite existing file "foo.txt".\n' == result.stderr
        assert state.describe_all() == self.restore_fs.save_state().describe_all()

    def test_when_user_reply_with_empty_string(self):
        self.restore_fs.add_trash_file('/cwd/parent/foo.txt',
                                       '/data_home/Trash',
                                       datetime.datetime(2016, 1, 1), 'boo')

        res = self.cmd_run(['trash-restore'], reply='', cwd='/cwd')

        assert res.last_line_of_stdout() == 'No files were restored'

    def test_with_no_args_and_no_files_in_trashcan(self):
        result = self.cmd_run(['trash-restore'], cwd='/cwd')

        assert result.all == \
               ("No files trashed from current dir ('/cwd')\n", '', None)

    def test_when_user_reply_with_not_number(self):
        self.restore_fs.add_trash_file('/cwd/parent/foo.txt',
                                       '/data_home/Trash',
                                       datetime.datetime(2016, 1, 1),
                                       b'boo')

        res = self.cmd_run(['trash-restore'], reply='non numeric', cwd='/cwd')

        assert res.last_line_of_stderr() == \
               'Invalid entry: not an index: non numeric'
        assert 1 == res.exit_code

    def test_should_print_version(self):
        result = self.cmd_run(['trash-restore', '--version'])

        assert result.output() == 'trash-restore 1.2.version\n'

    def cmd_run(self,
                args=None,  # type: Optional[List[str]]
                reply=None,
                cwd=None,
                ):  # type: (...) -> CmdResult
        args = [] if args is None else args
        user = RestoreUser(environ={'XDG_DATA_HOME': '/data_home'},
                           uid=999,
                           version="1.2.version",
                           volumes=self.restore_fs,
                           fs=self.fs,
                           restore_fs=self.restore_fs)
        return user.run_restore(args, reply, cwd)


def join_checks(*checks):
    result = []
    for check in checks:
        if check:
            result.append(check)
    return result
