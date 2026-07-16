import os
import unittest

import pytest

from tests.support.dirs.my_path import MyPath
from tests.support.restore.restore_file_fixture import RestoreFileFixture
from tests.support.restore.restore_user import RestoreUser
from trashcli.empty.top_trash_dir_rules_file_system_reader import RealTopTrashDirFs
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
            write_fs=RealRestoreWriterFs(),
            listing_fs=RealListFilesInDir(),
            version='0.0.0',
            volumes=FakeVolumes([]),
            top_trash_dir_rules_reader=RealTopTrashDirFs(),
        )

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
