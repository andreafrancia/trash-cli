import unittest

from mock import Mock, call
from six import StringIO

from trashcli.fs import contents_of
from trashcli.restore.file_system import RestoreFileSystem
from trashcli.restore.restore_cmd import RestoreCmd
from trashcli.restore.trash_directories import make_trash_directories, \
    TrashDirectory
from trashcli.restore.trashed_file import TrashedFile, TrashedFiles


def last_line_of(io):  # type: (StringIO) -> str
    return io.getvalue().splitlines()[-1]


class TestTrashRestoreCmd(unittest.TestCase):
    def setUp(self):
        self.stdout = StringIO()
        self.stderr = StringIO()
        trash_directories = make_trash_directories()
        self.logger = Mock(spec=[])
        self.trashed_files = TrashedFiles(self.logger,
                                          trash_directories,
                                          TrashDirectory(),
                                          contents_of)
        self.trashed_files.all_trashed_files = Mock(return_value=[])
        self.fs = Mock(spec=RestoreFileSystem)
        self.fs.getcwd_as_realpath = lambda: "cwd"
        self.cmd = RestoreCmd.make(stdout=self.stdout,
                                   stderr=self.stderr,
                                   exit=self.capture_exit_status,
                                   input=lambda x: self.user_reply,
                                   version='1.2.3',
                                   trashed_files=self.trashed_files,
                                   mount_points=lambda: [],
                                   fs=self.fs)

    def capture_exit_status(self, exit_status):
        self.exit_status = exit_status

    def test_should_print_version(self):
        self.cmd.run(['trash-restore', '--version'])

        assert 'trash-restore 1.2.3\n' == self.stdout.getvalue()

    def test_with_no_args_and_no_files_in_trashcan(self):
        self.cmd.curdir = lambda: "cwd"

        self.cmd.run(['trash-restore'])

        assert ("No files trashed from current dir ('cwd')\n" ==
                self.stdout.getvalue())

    def test_until_the_restore_unit(self):
        self.fs.path_exists.return_value = False
        self.set_trashed_files_to([a_trashed_file_in('cwd/parent/path')])

        self.user_reply = '0'
        self.cmd.run(['trash-restore'])

        assert '' == self.stderr.getvalue()
        assert [call.path_exists('cwd/parent/path'),
                call.mkdirs('cwd/parent'),
                call.move('orig_file', 'cwd/parent/path'),
                call.remove_file('info_file')] == self.fs.mock_calls

    def test_when_user_reply_with_empty_string(self):
        self.set_trashed_files_to([a_trashed_file])

        self.user_reply = ''
        self.cmd.run(['trash-restore'])

        assert last_line_of(self.stdout) == 'Exiting'

    def test_when_user_reply_with_not_number(self):
        self.set_trashed_files_to([a_trashed_file])

        self.user_reply = 'non numeric'
        self.cmd.run(['trash-restore'])

        assert last_line_of(self.stderr) == \
               'Invalid entry: not an index: non numeric'
        assert 1 == self.exit_status

    def set_trashed_files_to(self, trashed_files):
        self.trashed_files.all_trashed_files.return_value = trashed_files


a_trashed_file = TrashedFile("cwd/a_path", None, "info_file", "orig_file")


def a_trashed_file_in(path):
    return TrashedFile(path, None, 'info_file', 'orig_file')
