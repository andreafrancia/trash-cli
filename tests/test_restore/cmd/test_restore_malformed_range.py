import os

import pytest

from tests.support.put.fake_fs.fake_fs import FakeFs
from tests.support.restore.restore_file_fixture import RestoreFileFixture
from tests.support.restore.restore_user import RestoreUser
from tests.test_restore.support.recording_logger import RecordingLogger
from trashcli.empty.top_trash_dir_rules_file_system_reader import \
    RealTopTrashDirFs
from trashcli.fstab.volumes import FakeVolumes


@pytest.mark.slow
class TestRestoreMalformedRange:
    def setup_method(self):
        self.fs = FakeFs()
        self.fixture = RestoreFileFixture('/XDG_DATA_HOME', self.fs)
        self.user = RestoreUser(
            environ={'XDG_DATA_HOME': '/XDG_DATA_HOME'},
            uid=os.getuid(),
            file_reader=self.fs,
            path_read_fs=self.fs,
            read_fs=self.fs,
            write_fs=self.fs,
            listing_fs=self.fs,
            version='0.0.0',
            volumes=FakeVolumes([]),
            top_trash_dir_rules_reader=RealTopTrashDirFs(),
            logger=RecordingLogger())

    def test_a_range_with_two_dashes_gives_an_error_instead_of_crashing(self):
        self.fixture.having_a_trashed_file('/foo/bar')

        res = self.user.run_restore(reply='1-2-3', from_dir='/foo')

        assert res.stderr == 'Invalid entry: not an index: 2-3\n'

