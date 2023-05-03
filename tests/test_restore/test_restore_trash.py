import os
import unittest

import pytest

from .support.restore_trash_user import RestoreTrashUser

from ..support.files import make_file, require_empty_dir
from ..support.my_path import MyPath


@pytest.mark.slow
class TestRestoreTrash(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        require_empty_dir(self.tmp_dir / 'XDG_DATA_HOME')
        self.cwd = self.tmp_dir / "cwd"
        self.user = RestoreTrashUser(self.tmp_dir / 'XDG_DATA_HOME', self.cwd)

    def test_it_does_nothing_when_no_file_have_been_found_in_current_dir(self):
        self.user.chdir('/')

        self.user.run_restore()

        self.assertEqual("No files trashed from current dir ('/')\n",
                         self.user.stdout())

    def test_gives_an_error_on_not_a_number_input(self):
        self.user.having_a_trashed_file('/foo/bar')
        self.user.chdir('/foo')

        self.user.run_restore(with_user_typing='+@notanumber')

        self.assertEqual('Invalid entry: not an index: +@notanumber\n',
                         self.user.stderr())

    def test_it_gives_error_when_user_input_is_too_small(self):
        self.user.having_a_trashed_file('/foo/bar')
        self.user.chdir('/foo')

        self.user.run_restore(with_user_typing='1')

        self.assertEqual('Invalid entry: out of range 0..0: 1\n',
                         self.user.stderr())

    def test_it_gives_error_when_user_input_is_too_large(self):
        self.user.having_a_trashed_file('/foo/bar')
        self.user.chdir('/foo')

        self.user.run_restore(with_user_typing='1')

        self.assertEqual('Invalid entry: out of range 0..0: 1\n',
                         self.user.stderr())

    def test_it_shows_the_file_deleted_from_the_current_dir(self):
        self.user.having_a_trashed_file('/foo/bar')
        self.user.chdir('/foo')

        self.user.run_restore(with_user_typing='')

        self.assertEqual('   0 2000-01-01 00:00:01 /foo/bar\n'
                         'Exiting\n', self.user.stdout())
        self.assertEqual('', self.user.stderr())

    def test_it_restores_the_file_selected_by_the_user(self):
        self.user.having_a_file_trashed_from_current_dir('foo')
        self.user.chdir(self.cwd)

        self.user.run_restore(with_user_typing='0')

        self.file_should_have_been_restored(self.cwd / 'foo')

    def test_it_refuses_overwriting_existing_file(self):
        self.user.having_a_file_trashed_from_current_dir('foo')
        self.user.chdir(self.cwd)
        make_file(self.cwd / "foo")

        self.user.run_restore(with_user_typing='0')

        self.assertEqual('Refusing to overwrite existing file "foo".\n',
                         self.user.stderr())

    def file_should_have_been_restored(self, filename):
        assert os.path.exists(filename)

    def tearDown(self):
        self.tmp_dir.clean_up()
