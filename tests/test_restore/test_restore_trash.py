import os
import unittest

from six import StringIO

import pytest
from mock import Mock

from trashcli.fs import contents_of, remove_file
from trashcli.fstab import volume_of
from trashcli.restore.restore_cmd import RestoreCmd
from trashcli.restore.trash_directories import TrashDirectories2, \
    TrashDirectories, TrashDirectory
from trashcli.restore.trashed_file import TrashedFiles

from ..fake_trash_dir import trashinfo_content_default_date
from ..support.files import make_file, require_empty_dir
from ..support.my_path import MyPath
from trashcli.restore.file_system import FakeRestoreFileSystem


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


class RestoreTrashUser:
    def __init__(self, XDG_DATA_HOME, cwd):
        self.XDG_DATA_HOME = XDG_DATA_HOME
        self.out = StringIO()
        self.err = StringIO()
        self.cwd = cwd
        self.fs = FakeRestoreFileSystem()

    def chdir(self, dir):
        self.current_dir = dir
        self.fs.chdir(dir)

    def run_restore(self, with_user_typing=''):
        environ = {'XDG_DATA_HOME': self.XDG_DATA_HOME}
        trash_directories = TrashDirectories(volume_of, os.getuid(), environ)
        trash_directories2 = TrashDirectories2(volume_of, trash_directories)
        logger = Mock(spec=[])
        trashed_files = TrashedFiles(logger,
                                     trash_directories2,
                                     TrashDirectory(),
                                     contents_of)
        RestoreCmd.make(
            stdout=self.out,
            stderr=self.err,
            exit=[].append,
            input=lambda msg: with_user_typing,
            version='0.0.0',
            trashed_files=trashed_files,
            mount_points=lambda: [],
            fs=self.fs,
        ).run([])

    def having_a_file_trashed_from_current_dir(self, filename):
        self.having_a_trashed_file(os.path.join(self.cwd, filename))
        remove_file(filename)
        assert not os.path.exists(filename)

    def having_a_trashed_file(self, path):
        make_file('%s/info/foo.trashinfo' % self._trash_dir(),
                  trashinfo_content_default_date(path))
        make_file('%s/files/foo' % self._trash_dir())

    def _trash_dir(self):
        return "%s/Trash" % self.XDG_DATA_HOME

    def stdout(self):
        return self.out.getvalue()

    def stderr(self):
        return self.err.getvalue()
