import unittest

from six import StringIO

from mock import Mock, call
from trashcli import restore
from trashcli.fs import contents_of
from trashcli.restore import (
    RestoreCmd,
    TrashDirectory,
    TrashedFile,
    TrashedFiles,
    make_trash_directories,
)


class TestTrashRestoreCmd(unittest.TestCase):
    def setUp(self):
        self.stdout = StringIO()
        self.stderr = StringIO()
        trash_directories = make_trash_directories()
        self.logger = Mock(spec=[])
        trashed_files = TrashedFiles(self.logger,
                                     trash_directories,
                                     TrashDirectory(),
                                     contents_of)
        self.fs = Mock(spec=restore.FileSystem)
        self.cmd = RestoreCmd(stdout=self.stdout,
                              stderr=self.stderr,
                              exit=self.capture_exit_status,
                              input=lambda x: self.user_reply,
                              version=None,
                              trashed_files=trashed_files,
                              mount_points=lambda: [],
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
