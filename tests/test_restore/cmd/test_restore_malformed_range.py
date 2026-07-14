import os
import unittest

import pytest

from tests.support.dirs.my_path import MyPath
from tests.support.restore.restore_file_fixture import RestoreFileFixture
from tests.support.restore.restore_user import RestoreUser
from trashcli.fslib.real_fs_operations import RealListFilesInDir
from trashcli.fstab.volumes import FakeVolumes
from trashcli.restore.real_restore_fs import RealFileReaderFs, \
    RealPathReaderFs, RealRestoreWriterFs, RealRestoreReadFs


@pytest.mark.slow
class TestRestoreMalformedRange(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.fixture = RestoreFileFixture(self.tmp_dir / 'XDG_DATA_HOME')
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

    def test_a_range_with_two_dashes_gives_an_error_instead_of_crashing(self):
        self.fixture.having_a_trashed_file('/foo/bar')

        res = self.user.run_restore(reply='1-2-3', from_dir='/foo')

        self.assertEqual('Invalid entry: not an index: 2-3\n', res.stderr)

    def tearDown(self):
        self.tmp_dir.clean_up()
