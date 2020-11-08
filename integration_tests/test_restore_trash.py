import os
import unittest
from trashcli.restore import RestoreCmd
from .files import require_empty_dir
from trashcli.fs import remove_file
from .trashinfo import a_trashinfo
from .files import write_file
from unit_tests.myStringIO import StringIO


class TestRestoreTrash(unittest.TestCase):
    def test_it_does_nothing_when_no_file_have_been_found_in_current_dir(self):
        self.user.chdir('/')

        self.user.run_restore()

        self.assertEqual("No files trashed from current dir ('/')\n",
                         self.user.stdout())

    def test_gives_an_error_on_not_a_number_input(self):
        self.having_a_trashed_file('/foo/bar')
        self.user.chdir('/foo')

        self.user.run_restore(with_user_typing='-@notanumber')

        self.assertEqual('Invalid entry\n', self.user.stderr())

    def test_it_gives_error_when_user_input_is_too_small(self):
        self.having_a_trashed_file('/foo/bar')
        self.user.chdir('/foo')

        self.user.run_restore(with_user_typing='-1')

        self.assertEqual('Invalid entry\n', self.user.stderr())

    def test_it_gives_error_when_user_input_is_too_large(self):
        self.having_a_trashed_file('/foo/bar')
        self.user.chdir('/foo')

        self.user.run_restore(with_user_typing='1')

        self.assertEqual('Invalid entry\n', self.user.stderr())

    def test_it_shows_the_file_deleted_from_the_current_dir(self):
        self.having_a_trashed_file('/foo/bar')
        self.user.chdir('/foo')

        self.user.run_restore(with_user_typing='')

        self.assertEqual('   0 2000-01-01 00:00:01 /foo/bar\n'
                         'Exiting\n', self.user.stdout())
        self.assertEqual('', self.user.stderr())

    def test_it_restores_the_file_selected_by_the_user(self):
        self.having_a_file_trashed_from_current_dir('foo')
        self.user.chdir(os.getcwd())

        self.user.run_restore(with_user_typing='0')

        self.file_should_have_been_restored('foo')

    def test_it_refuses_overwriting_existing_file(self):
        self.having_a_file_trashed_from_current_dir('foo')
        self.user.chdir(os.getcwd())
        write_file("foo")

        self.user.run_restore(with_user_typing='0')

        self.assertEqual('Refusing to overwrite existing file "foo".\n',
                         self.user.stderr())

    def setUp(self):
        require_empty_dir('XDG_DATA_HOME')

        trashcan = TrashCan('XDG_DATA_HOME/Trash')
        self.having_a_trashed_file = trashcan.write_trashed_file

        self.user = RestoreTrashUser('XDG_DATA_HOME')

    def having_a_file_trashed_from_current_dir(self, filename):
        self.having_a_trashed_file(os.path.join(os.getcwd(), filename))
        remove_file(filename)
        assert not os.path.exists(filename)

    def file_should_have_been_restored(self, filename):
        assert os.path.exists(filename)


class RestoreTrashUser:
    def __init__(self, XDG_DATA_HOME):
        self.environ = {'XDG_DATA_HOME': XDG_DATA_HOME}
        self.out = StringIO()
        self.err = StringIO()

    def chdir(self, dir):
        self.current_dir = dir

    def run_restore(self, with_user_typing=''):
        RestoreCmd(
            stdout  = self.out,
            stderr  = self.err,
            environ = self.environ,
            exit    = [].append,
            input   = lambda msg: with_user_typing,
            curdir  = lambda: self.current_dir
        ).run([])

    def stdout(self):
        return self.out.getvalue()

    def stderr(self):
        return self.err.getvalue()


class TrashCan:
    def __init__(self, path):
        self.path = path

    def write_trashed_file(self, path):
        write_file('%s/info/foo.trashinfo' % self.path, a_trashinfo(path))
        write_file('%s/files/foo' % self.path)
