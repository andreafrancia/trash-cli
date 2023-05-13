import os
import unittest

import pytest

from tests.support.asserts.assert_that import assert_that
from tests.support.my_path import MyPath
from tests.test_restore.support.a_trashed_file import ATrashedFile
from tests.test_restore.support.has_been_restored_matcher import \
    has_been_restored
from tests.test_restore.support.restore_file_fixture import RestoreFileFixture
from tests.test_restore.support.restore_user import RestoreUser
from trashcli.fs import FsMethods
from trashcli.fstab.volumes import FakeVolumes
from trashcli.restore.file_system import RealFileReader, \
    RealRestoreReadFileSystem, RealRestoreWriteFileSystem, RealListingFileSystem


@pytest.mark.slow
class TestRestoreTrash(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.fixture = RestoreFileFixture(self.tmp_dir / 'XDG_DATA_HOME')
        self.fs = FsMethods()
        self.cwd = self.tmp_dir / "cwd"
        XDG_DATA_HOME = self.tmp_dir / 'XDG_DATA_HOME'
        self.trash_dir = XDG_DATA_HOME / 'Trash'
        self.user = RestoreUser(environ={'XDG_DATA_HOME': XDG_DATA_HOME},
                                uid=os.getuid(),
                                file_reader=RealFileReader(),
                                read_fs=RealRestoreReadFileSystem(),
                                write_fs=RealRestoreWriteFileSystem(),
                                listing_file_system=RealListingFileSystem(),
                                version='0.0.0',
                                volumes=FakeVolumes([]))

    def test_it_does_nothing_when_no_file_have_been_found_in_current_dir(self):
        res = self.user.run_restore(from_dir='/')

        self.assertEqual("No files trashed from current dir ('/')\n",
                         res.output())

    def test_gives_an_error_on_not_a_number_input(self):
        self.fixture.having_a_trashed_file('/foo/bar')

        res = self.user.run_restore(reply='+@notanumber', from_dir='/foo')

        self.assertEqual('Invalid entry: not an index: +@notanumber\n',
                         res.stderr)

    def test_it_gives_error_when_user_input_is_too_small(self):
        self.fixture.having_a_trashed_file('/foo/bar')

        res = self.user.run_restore(reply='1', from_dir='/foo')

        self.assertEqual('Invalid entry: out of range 0..0: 1\n',
                         res.stderr)

    def test_it_gives_error_when_user_input_is_too_large(self):
        self.fixture.having_a_trashed_file('/foo/bar')

        res = self.user.run_restore(reply='1', from_dir='/foo')

        self.assertEqual('Invalid entry: out of range 0..0: 1\n',
                         res.stderr)

    def test_it_shows_the_file_deleted_from_the_current_dir(self):
        self.fixture.having_a_trashed_file('/foo/bar')

        res = self.user.run_restore(reply='', from_dir='/foo')

        self.assertEqual('   0 2000-01-01 00:00:01 /foo/bar\n'
                         'Exiting\n', res.output())
        self.assertEqual('', res.stderr)

    def test_it_restores_the_file_selected_by_the_user(self):
        self.fixture.having_a_trashed_file(self.cwd / 'foo')

        self.user.run_restore(reply='0', from_dir=self.cwd)

        self.fixture.file_should_have_been_restored(self.cwd / 'foo')

    def test_it_refuses_overwriting_existing_file(self):
        self.fixture.having_a_trashed_file(self.cwd / 'foo')
        self.fixture.make_file(self.cwd / "foo")

        res = self.user.run_restore(reply='0', from_dir=self.cwd)

        self.assertEqual('Refusing to overwrite existing file "foo".\n',
                         res.stderr)

    def test_it_restores_the_file_and_delete_the_trash_info(self):
        a_trashed_file = self.make_trashed_file()

        res = self.user.run_restore(reply='0', from_dir=self.cwd)

        assert res.stderr == ''
        assert_that(a_trashed_file, has_been_restored(self.fs))

    def make_trashed_file(self):  # type: () -> ATrashedFile
        original_location = self.cwd / 'parent/path'
        backup_copy = self.trash_dir / 'files/path'
        info_file = self.trash_dir / 'info/path.trashinfo'

        self.fixture.make_file(info_file,
                               '[Trash Info]\n'
                               'Path=%s\n' % original_location +
                               'DeletionDate=2000-01-01T00:00:01\n')
        self.fixture.make_empty_file(backup_copy)

        return ATrashedFile(
            trashed_from=self.cwd / 'parent/path',
            info_file=self.trash_dir / 'info/path.trashinfo',
            backup_copy=self.trash_dir / 'files/path',
        )

    def tearDown(self):
        self.tmp_dir.clean_up()
