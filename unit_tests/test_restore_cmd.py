from trashcli.restore import RestoreCmd
from nose.tools import assert_equals
from StringIO import StringIO

class TestTrashRestoreCmd:
    def setUp(self):
        self.stdout = StringIO()
        self.stderr = StringIO()
        self.cmd = RestoreCmd(stdout=self.stdout,
                              stderr=self.stderr,
                              environ=None,
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
        self.cmd.trashcan.home_trashcan.environ = {}
        self.cmd.curdir = lambda: "cwd"

        self.cmd.run(['trash-restore'])

        assert_equals("No files trashed from current dir ('cwd')\n",
                self.stdout.getvalue())

    def test_with_no_args_and_files_in_trashcan(self):
        class thing(object):
            pass
        def some_files(append, _):
            t = thing()
            t.deletion_date = None
            t.path = None
            append(t)
        self.cmd.trashcan.home_trashcan.environ = {}
        self.cmd.curdir = lambda: "cwd"
        self.cmd.for_all_trashed_file_in_dir = some_files
        self.cmd.input = lambda _ : ""

        self.cmd.run(['trash-restore'])

        assert_equals("   0 None None\n"
                "Exiting\n",
                self.stdout.getvalue())
    def test_when_user_reply_with_empty_string(self):
        self.user_reply = ''

        self.cmd.restore_asking_the_user([])

        assert_equals('Exiting\n', self.stdout.getvalue())

    def test_when_user_reply_with_empty_string(self):
        self.user_reply = 'non numeric'

        self.cmd.restore_asking_the_user([])

        assert_equals('Invalid entry\n', self.stderr.getvalue())
        assert_equals('', self.stdout.getvalue())
        assert_equals(1, self.exit_status)

    def test_when_user_reply_with_out_of_range_number(self):
        self.user_reply = '100'

        self.cmd.restore_asking_the_user([])

        assert_equals('Invalid entry\n', self.stderr.getvalue())
        assert_equals('', self.stdout.getvalue())
        assert_equals(1, self.exit_status)

from trashcli.restore import TrashedFile
from nose.tools import assert_raises, assert_true
import os
class TestTrashedFileRestore:
    def setUp(self):
        self.remove_file_if_exists('parent/path')
        self.remove_dir_if_exists('parent')

    def test_restore(self):
        trashed_file = TrashedFile('parent/path',
                                   None,
                                   'info_file',
                                   'orig',
                                   None)
        open('orig','w').close()
        open('info_file','w').close()

        trashed_file.restore()

        assert_true(os.path.exists('parent/path'))
        assert_true(not os.path.exists('info_file'))

    def test_restore_over_existing_file(self):
        trashed_file = TrashedFile('path',None,None,None,None)
        open('path','w').close()

        assert_raises(IOError, trashed_file.restore)

    def tearDown(self):
        self.remove_file_if_exists('path')
        self.remove_file_if_exists('parent/path')
        self.remove_dir_if_exists('parent')

    def remove_file_if_exists(self, path):
        if os.path.lexists(path):
            os.unlink(path)
    def remove_dir_if_exists(self, dir):
        if os.path.exists(dir):
            os.rmdir(dir)
