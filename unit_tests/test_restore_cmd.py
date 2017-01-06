from trashcli.restore import RestoreCmd
from nose.tools import assert_equals
from .myStringIO import StringIO
from mock import Mock, call

class TestListingInRestoreCmd:
    def setUp(self):
        self.cmd = RestoreCmd(None, None, None, None, None)
        self.cmd.curdir = lambda: "dir"
        self.cmd.handle_trashed_files = self.capture_trashed_files

    def test_with_no_args_and_files_in_trashcan(self):
        def some_files():
            yield FakeTrashedFile('<date>', 'dir/location')
            yield FakeTrashedFile('<date>', 'dir/location')
            yield FakeTrashedFile('<date>', 'anotherdir/location')

        self.cmd.all_trashed_files = some_files

        self.cmd.run(['trash-restore'])

        assert_equals([
            'dir/location'
            , 'dir/location'
            ] ,self.original_locations)

    def test_with_no_args_and_files_in_trashcan(self):
        def some_files():
            yield FakeTrashedFile('<date>', 'dir/location')
            yield FakeTrashedFile('<date>', 'dir/location')
            yield FakeTrashedFile('<date>', 'specific/path')

        self.cmd.all_trashed_files = some_files

        self.cmd.run(['trash-restore', 'specific/path'])

        assert_equals([
            'specific/path'
            ] ,self.original_locations)

    def capture_trashed_files(self,arg):
        self.original_locations = []
        for trashed_file in arg:
            self.original_locations.append(trashed_file.original_location)


class FakeTrashedFile(object):
    def __init__(self, deletion_date, original_location):
        self.deletion_date = deletion_date
        self.original_location = original_location
    def __repr__(self):
        return ('FakeTrashedFile(\'%s\', ' % self.deletion_date +
               '\'%s\')' % self.original_location)

class TestTrashRestoreCmd:
    def setUp(self):
        self.stdout = StringIO()
        self.stderr = StringIO()
        self.cmd = RestoreCmd(stdout=self.stdout,
                              stderr=self.stderr,
                              environ={},
                              exit = self.capture_exit_status,
                              input =lambda x: self.user_reply,
                              version = None)

    def capture_exit_status(self, exit_status):
        self.exit_status = exit_status

    def test_should_print_version(self):
        self.cmd.version = '1.2.3'
        self.cmd.run(['trash-restore', '--version'])

        assert_equals('trash-restore 1.2.3\n', self.stdout.getvalue())

    def test_with_no_args_and_no_files_in_trashcan(self):
        self.cmd.curdir = lambda: "cwd"

        self.cmd.run(['trash-restore'])

        assert_equals("No files trashed from current dir ('cwd')\n",
                self.stdout.getvalue())

    def test_until_the_restore_intgration(self):
        from trashcli.fs import remove_file
        from trashcli.fs import contents_of
        self.user_reply = '0'
        open('orig_file', 'w').write('original')
        open('info_file', 'w').write('')
        remove_file('parent/path')
        remove_file('parent')

        trashed_file = TrashedFile(
                'parent/path',
                None,
                'info_file',
                'orig_file')

        self.cmd.restore_asking_the_user([trashed_file])

        assert_equals('', self.stdout.getvalue())
        assert_equals('', self.stderr.getvalue())
        assert_true(not os.path.exists('info_file'))
        assert_true(not os.path.exists('orig_file'))
        assert_true(os.path.exists('parent/path'))
        assert_equals('original', contents_of('parent/path'))

    def test_until_the_restore_unit(self):
        trashed_file = TrashedFile(
                'parent/path',
                None,
                'info_file',
                'orig_file')
        fs = Mock()
        self.cmd.fs = fs
        self.cmd.path_exists = lambda _: False

        self.user_reply = '0'
        self.cmd.restore_asking_the_user([trashed_file])

        assert_equals('', self.stdout.getvalue())
        assert_equals('', self.stderr.getvalue())
        assert_equals([
            call.mkdirs('parent')
            , call.move('orig_file', 'parent/path')
            , call.remove_file('info_file')
            ], fs.mock_calls)

    def test_when_user_reply_with_empty_string(self):
        self.user_reply = ''

        self.cmd.restore_asking_the_user([])

        assert_equals('Exiting\n', self.stdout.getvalue())

    def test_when_user_reply_with_not_number(self):
        self.user_reply = 'non numeric'

        self.cmd.restore_asking_the_user([])

        assert_equals('Invalid entry\n', self.stderr.getvalue())
        assert_equals('', self.stdout.getvalue())
        assert_equals(1, self.exit_status)

    def test_when_user_reply_with_an_out_of_range_number(self):
        self.user_reply = '100'

        self.cmd.restore_asking_the_user([])

        assert_equals('Invalid entry\n', self.stderr.getvalue())
        assert_equals('', self.stdout.getvalue())
        assert_equals(1, self.exit_status)

from trashcli.restore import TrashedFile
from nose.tools import assert_raises, assert_true
import os
class TestTrashedFileRestoreIntegration:
    def setUp(self):
        remove_file_if_exists('parent/path')
        remove_dir_if_exists('parent')
        self.cmd = RestoreCmd(None, None, None, None, None)

    def test_restore(self):
        trashed_file = TrashedFile('parent/path',
                                   None,
                                   'info_file',
                                   'orig')
        open('orig','w').close()
        open('info_file','w').close()

        self.cmd.restore(trashed_file)

        assert_true(os.path.exists('parent/path'))
        assert_true(not os.path.exists('info_file'))

    def test_restore_over_existing_file(self):
        trashed_file = TrashedFile('path',None,None,None)
        open('path','w').close()

        assert_raises(IOError, lambda:
                self.cmd.restore(trashed_file))

    def tearDown(self):
        remove_file_if_exists('path')
        remove_file_if_exists('parent/path')
        remove_dir_if_exists('parent')

    def test_restore_create_needed_directories(self):
        require_empty_dir('sandbox')

        write_file('sandbox/TrashDir/files/bar')
        instance = TrashedFile('sandbox/foo/bar',
                               'deletion_date', 'info_file',
                               'sandbox/TrashDir/files/bar')
        self.cmd.restore(instance)
        assert os.path.exists("sandbox/foo/bar")

import datetime
from mock import Mock
class TestRestoreCmdListingUnit:
    def test_something(self):
        cmd = RestoreCmd(None, None, {}, None, None)
        cmd.contents_of = lambda path: 'Path=name\nDeletionDate=2001-01-01T10:10:10'
        path_to_trashinfo = 'info/info_path.trashinfo'
        trash_dir = Mock([])
        trash_dir.volume = '/volume'
        trash_dir.all_info_files = Mock([], return_value=[path_to_trashinfo])
        cmd.all_trash_directories2 = lambda: [trash_dir]

        cmd.curdir = lambda: '/volume'
        trashed_files = list(cmd.all_trashed_files())

        trashed_file = trashed_files[0]
        assert_equals('/volume/name' , trashed_file.original_location)
        assert_equals(datetime.datetime(2001, 1, 1, 10, 10, 10),
                      trashed_file.deletion_date)
        assert_equals('info/info_path.trashinfo' , trashed_file.info_file)
        assert_equals('files/info_path' , trashed_file.original_file)

from integration_tests.files import write_file, require_empty_dir
from trashcli.fs import remove_file
class TestRestoreCmdListingIntegration:
    def test_something(self):
        cmd = RestoreCmd(None, None, {}, None, None)
        require_empty_dir('info')
        open('info/info_path.trashinfo', 'w').write(
                'Path=name\nDeletionDate=2001-01-01T10:10:10')
        path_to_trashinfo = 'info/info_path.trashinfo'
        trash_dir = Mock([])
        trash_dir.volume = '/volume'
        trash_dir.all_info_files = Mock([], return_value=[path_to_trashinfo])
        cmd.all_trash_directories2 = lambda: [trash_dir]

        cmd.curdir = lambda: '/volume'
        trashed_files = list(cmd.all_trashed_files())

        trashed_file = trashed_files[0]
        assert_equals('/volume/name' , trashed_file.original_location)
        assert_equals(datetime.datetime(2001, 1, 1, 10, 10, 10),
                      trashed_file.deletion_date)
        assert_equals('info/info_path.trashinfo' , trashed_file.info_file)
        assert_equals('files/info_path' , trashed_file.original_file)

    def tearDown(self):
        remove_file('info/info_path.trashinfo')
        remove_dir_if_exists('info')

def remove_dir_if_exists(dir):
    if os.path.exists(dir):
        os.rmdir(dir)
def remove_file_if_exists(path):
    if os.path.lexists(path):
        os.unlink(path)


