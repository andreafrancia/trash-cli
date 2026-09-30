import os

import pytest

from tests.support.dirs.my_path import MyPath
from tests.support.restore.restore_file_fixture import RestoreFileFixture
from tests.support.restore.restore_user import RestoreUser
from tests.test_restore.support.recording_logger import RecordingLogger
from trashcli.empty.top_trash_dir_rules_file_system_reader import \
    RealTopTrashDirFs
from trashcli.fslib.real_fs_operations import RealListFilesInDir
from trashcli.fstab.volumes import FakeVolumes
from trashcli.put.fs.real_fs import RealFs
from trashcli.put.fs.real_volume_path_fs import RealVolumePathFs
from trashcli.restore.real_restore_fs import RealFileReaderFs, \
    RealPathReaderFs, RealRestoreWriterFs, RealRestoreReadFs


@pytest.mark.slow
class TestRestoreMalformedRange:
    def setup_method(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.fixture = RestoreFileFixture(self.tmp_dir / 'XDG_DATA_HOME',
                                          RealFs())
        self.user = RestoreUser(
            environ={'XDG_DATA_HOME': self.tmp_dir / 'XDG_DATA_HOME'},
            uid=os.getuid(),
            file_reader=RealFileReaderFs(),
            path_read_fs=RealPathReaderFs(),
            read_fs=RealRestoreReadFs(),
            write_fs=RealRestoreWriterFs(),
            listing_fs=RealListFilesInDir(),
            version='0.0.0',
            volumes=FakeVolumes([]),
            volume_path_fs=RealVolumePathFs(),
            top_trash_dir_rules_reader=RealTopTrashDirFs(),
            logger=RecordingLogger())

    def test_a_range_with_two_dashes_gives_an_error_instead_of_crashing(self):
        self.fixture.having_a_trashed_file('/foo/bar')

        res = self.user.run_restore(reply='1-2-3', from_dir='/foo')

        assert res.stderr == 'Invalid entry: not an index: 2-3\n'

    def teardown_method(self):
        self.tmp_dir.clean_up()
