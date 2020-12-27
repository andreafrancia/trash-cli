import unittest
from argparse import Namespace

from trashcli.list_mount_points import os_mount_points
from trashcli.restore import RestoreCmd, make_trash_directories, \
    TrashDirectory, TrashedFiles, Command
from .myStringIO import StringIO
from mock import call
from trashcli import restore
import datetime
from mock import Mock
from integration_tests.files import make_file, require_empty_dir
from trashcli.fs import remove_file
from trashcli.fs import contents_of
from trashcli.restore import TrashedFile
import os


class Test_parse_args(unittest.TestCase):
    def test_default_path(self):

        args = restore.parse_args([''], "curdir")

        self.assertEqual((Command.RunRestore,
                          {'path': 'curdir',
                           'sort': 'date',
                           'trash_dir': None}),
                         args)

    def test_path_specified_relative_path(self):

        args = restore.parse_args(['', 'path'], "curdir")

        self.assertEqual((Command.RunRestore,
                          {'path': 'path',
                           'sort': 'date',
                           'trash_dir': None}),
                         args)

    def test_path_specified_fullpath(self):

        args = restore.parse_args(['', '/a/path'], "ignored")

        self.assertEqual((Command.RunRestore,
                          {'path': '/a/path',
                           'sort': 'date',
                           'trash_dir': None}),
                         args)

    def test_show_version(self):
        args = restore.parse_args(['', '--version'], "ignored")

        self.assertEqual((Command.PrintVersion, None), args)

class TestListingInRestoreCmd(unittest.TestCase):
    def setUp(self):
        trash_directories = make_trash_directories()
        trashed_files = TrashedFiles(trash_directories, None, contents_of)
        self.cmd = RestoreCmd(None, None,
                              exit=None,
                              input=None,
                              curdir=lambda: "dir",
                              trashed_files=trashed_files,
                              mount_points=os_mount_points,
                              fs=restore.FileSystem())
        self.cmd.handle_trashed_files = self.capture_trashed_files
        self.trashed_files = Mock(spec=['all_trashed_files'])
        self.cmd.trashed_files = self.trashed_files

    def test_with_no_args_and_files_in_trashcan(self):
        self.trashed_files.all_trashed_files.return_value = [
            FakeTrashedFile('<date>', 'dir/location'),
            FakeTrashedFile('<date>', 'dir/location'),
            FakeTrashedFile('<date>', 'anotherdir/location')
        ]

        self.cmd.run(['trash-restore'])

        assert [
            'dir/location'
            , 'dir/location'
            ] ==self.original_locations

    def test_with_no_args_and_files_in_trashcan_2(self):
        self.trashed_files.all_trashed_files.return_value = [
            FakeTrashedFile('<date>', 'dir/location'),
            FakeTrashedFile('<date>', 'dir/location'),
            FakeTrashedFile('<date>', 'specific/path'),
        ]

        self.cmd.run(['trash-restore', 'specific/path'])

        assert [
            'specific/path'
            ] ==self.original_locations

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


class TestTrashRestoreCmd(unittest.TestCase):
    def setUp(self):
        self.stdout = StringIO()
        self.stderr = StringIO()
        trash_directories = make_trash_directories()
        trashed_files = TrashedFiles(trash_directories, TrashDirectory(),
                                     contents_of)
        self.fs = Mock(spec=restore.FileSystem)
        self.cmd = RestoreCmd(stdout=self.stdout,
                              stderr=self.stderr,
                              exit = self.capture_exit_status,
                              input =lambda x: self.user_reply,
                              version=None,
                              trashed_files=trashed_files,
                              mount_points=os_mount_points,
                              fs=self.fs)

    def capture_exit_status(self, exit_status):
        self.exit_status = exit_status

    def test_should_print_version(self):
        self.cmd.version = '1.2.3'
        self.cmd.run(['trash-restore', '--version'])

        assert 'trash-restore 1.2.3\n' == self.stdout.getvalue()

    def test_with_no_args_and_no_files_in_trashcan(self):
        self.cmd.curdir = lambda: "cwd"

        self.cmd.run(['trash-restore'])

        assert ("No files trashed from current dir ('cwd')\n" ==
                self.stdout.getvalue())

    def test_until_the_restore_unit(self):
        self.fs.path_exists.return_value = False
        trashed_file = TrashedFile(
                'parent/path',
                None,
                'info_file',
                'orig_file')

        self.user_reply = '0'
        self.cmd.restore_asking_the_user([trashed_file])

        assert '' == self.stdout.getvalue()
        assert '' == self.stderr.getvalue()
        assert [call.path_exists('parent/path'),
                      call.mkdirs('parent'),
                      call.move('orig_file', 'parent/path'),
                      call.remove_file('info_file')] == self.fs.mock_calls

    def test_when_user_reply_with_empty_string(self):
        self.user_reply = ''

        self.cmd.restore_asking_the_user([])

        assert 'Exiting\n' == self.stdout.getvalue()

    def test_when_user_reply_with_not_number(self):
        self.user_reply = 'non numeric'

        self.cmd.restore_asking_the_user([])

        assert 'Invalid entry: not an index: non numeric\n' == \
               self.stderr.getvalue()
        assert '' == self.stdout.getvalue()
        assert 1 == self.exit_status


class TestTrashedFileRestoreIntegration(unittest.TestCase):
    def setUp(self):
        remove_file_if_exists('parent/path')
        remove_dir_if_exists('parent')
        trash_directories = make_trash_directories()
        trashed_files = TrashedFiles(trash_directories, TrashDirectory(),
                                     contents_of)
        self.cmd = RestoreCmd(None,
                              None,
                              exit=None,
                              input=None,
                              trashed_files=trashed_files,
                              mount_points=os_mount_points,
                              fs=restore.FileSystem())

    def test_restore(self):
        trashed_file = TrashedFile('parent/path',
                                   None,
                                   'info_file',
                                   'orig')
        open('orig','w').close()
        open('info_file','w').close()

        self.cmd.restore(trashed_file)

        assert os.path.exists('parent/path')
        assert not os.path.exists('info_file')

    def test_restore_over_existing_file(self):
        trashed_file = TrashedFile('path',None,None,None)
        open('path','w').close()

        self.assertRaises(IOError, lambda:self.cmd.restore(trashed_file))

    def tearDown(self):
        remove_file_if_exists('path')
        remove_file_if_exists('parent/path')
        remove_dir_if_exists('parent')

    def test_restore_create_needed_directories(self):
        require_empty_dir('sandbox')

        make_file('sandbox/TrashDir/files/bar')
        instance = TrashedFile('sandbox/foo/bar',
                               'deletion_date', 'info_file',
                               'sandbox/TrashDir/files/bar')
        self.cmd.restore(instance)
        assert os.path.exists("sandbox/foo/bar")


class TestTrashedFiles(unittest.TestCase):
    def setUp(self):
        self.trash_directories = Mock(spec=['trash_directories_or_user'])
        self.trash_directory = Mock(spec=['all_info_files'])
        self.contents_of = Mock()
        self.trashed_files = TrashedFiles(self.trash_directories,
                                          self.trash_directory,
                                          self.contents_of)

    def test_something(self):
        self.trash_directories.trash_directories_or_user.return_value = \
            [("path", "/volume")]
        self.contents_of.return_value='Path=name\nDeletionDate=2001-01-01T10:10:10'
        self.trash_directory.all_info_files.return_value = \
            [('trashinfo', 'info/info_path.trashinfo')]

        trashed_files = list(self.trashed_files.all_trashed_files([], None))

        trashed_file = trashed_files[0]
        assert '/volume/name' == trashed_file.original_location
        assert (datetime.datetime(2001, 1, 1, 10, 10, 10) ==
                     trashed_file.deletion_date)
        assert 'info/info_path.trashinfo' == trashed_file.info_file
        assert 'files/info_path' == trashed_file.original_file
        assert ([call.trash_directories_or_user([], None)] ==
                     self.trash_directories.mock_calls)


class TestTrashedFilesIntegration(unittest.TestCase):
    def setUp(self):
        self.trash_directories = Mock(spec=['trash_directories_or_user'])
        self.trash_directory = Mock(spec=['all_info_files'])
        self.trashed_files = TrashedFiles(self.trash_directories,
                                          self.trash_directory,
                                          contents_of)

    def test_something(self):
        require_empty_dir('info')
        self.trash_directories.trash_directories_or_user.return_value = \
            [("path", "/volume")]
        open('info/info_path.trashinfo', 'w').write(
                'Path=name\nDeletionDate=2001-01-01T10:10:10')
        self.trash_directory.all_info_files = Mock([], return_value=[
            ('trashinfo', 'info/info_path.trashinfo')])

        trashed_files = list(self.trashed_files.all_trashed_files([], None))

        trashed_file = trashed_files[0]
        assert '/volume/name' == trashed_file.original_location
        assert (datetime.datetime(2001, 1, 1, 10, 10, 10) ==
                     trashed_file.deletion_date)
        assert 'info/info_path.trashinfo' == trashed_file.info_file
        assert 'files/info_path' == trashed_file.original_file

    def tearDown(self):
        remove_file('info/info_path.trashinfo')
        remove_dir_if_exists('info')

def remove_dir_if_exists(dir):
    if os.path.exists(dir):
        os.rmdir(dir)
def remove_file_if_exists(path):
    if os.path.lexists(path):
        os.unlink(path)


