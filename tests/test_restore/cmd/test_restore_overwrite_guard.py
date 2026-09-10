import os
import unittest

import pytest

from tests.support.dirs.my_path import MyPath
from tests.support.fakes.fake_trash_dir import trashinfo_content_default_date
from tests.support.restore.restore_file_fixture import RestoreFileFixture
from tests.support.restore.restore_user import RestoreUser
from trashcli.fslib.real_fs_operations import RealListFilesInDir
from trashcli.fstab.volumes import FakeVolumes
from trashcli.restore.real_restore_fs import RealFileReaderFs, \
    RealPathReaderFs, RealRestoreWriterFs, RealRestoreReadFs


@pytest.mark.slow
class TestRestoreOverwriteGuard(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.fixture = RestoreFileFixture(self.tmp_dir / 'XDG_DATA_HOME')
        self.cwd = self.tmp_dir / 'cwd'
        os.makedirs(self.cwd)
        self.user = RestoreUser(
            environ={'XDG_DATA_HOME': self.tmp_dir / 'XDG_DATA_HOME'},
            uid=os.getuid(),
            file_reader=RealFileReaderFs(),
            path_read_fs=RealPathReaderFs(),
            read_fs=RealRestoreReadFs(),
            write_fs=RealRestoreWriterFs(),
            listing_fs=RealListFilesInDir(),
            version='0.0.0',
            volumes=FakeVolumes([]))

    def test_it_refuses_to_restore_over_a_dangling_symlink(self):
        self.fixture.having_a_trashed_file(self.cwd / 'foo')
        os.symlink(self.cwd / 'this-target-does-not-exist', self.cwd / 'foo')

        res = self.user.run_restore(reply='0', from_dir=self.cwd)

        self.assertEqual('Refusing to overwrite existing file "foo".\n',
                         res.stderr)

    def test_it_refuses_to_restore_onto_a_directory_even_with_overwrite(self):
        self.fixture.having_a_trashed_file(self.cwd / 'foo')
        os.makedirs(self.cwd / 'foo')

        res = self.user.run_restore(args=['trash-restore', '--overwrite'],
                                    reply='0', from_dir=self.cwd)

        self.assertEqual('Refusing to overwrite existing file "foo".\n',
                         res.stderr)

    def tearDown(self):
        self.tmp_dir.clean_up()

    def test_batch_keeps_conflicting_entry_and_restores_the_next_file(self):
        trash = self.tmp_dir / 'XDG_DATA_HOME/Trash'
        for name in ['a', 'b']:
            self.fixture.make_file(trash / ('info/' + name + '.trashinfo'),
                                   trashinfo_content_default_date(self.cwd / name))
            self.fixture.make_file(trash / ('files/' + name), 'trashed ' + name)
        self.fixture.make_file(self.cwd / 'a', 'existing a')

        res = self.user.run_restore(args=['trash-restore', '--sort=path'],
                                    reply='0-1', from_dir=self.cwd)

        self.assertEqual(1, res.exit_code)
        self.assertEqual('Refusing to overwrite existing file "a".\n', res.stderr)
        with open(self.cwd / 'a') as restored:
            self.assertEqual('existing a', restored.read())
        with open(self.cwd / 'b') as restored:
            self.assertEqual('trashed b', restored.read())
        with open(trash / 'files/a') as remaining:
            self.assertEqual('trashed a', remaining.read())
        self.assertTrue(os.path.exists(trash / 'info/a.trashinfo'))
        self.assertFalse(os.path.exists(trash / 'files/b'))
        self.assertFalse(os.path.exists(trash / 'info/b.trashinfo'))
