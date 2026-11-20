import pytest

from tests.support.fs_fixture import fake_fs_fixture
from tests.support.restore.restore_file_fixture import RestoreFileFixture
from tests.support.restore.restore_user import RestoreUser
from tests.test_restore.support.recording_logger import RecordingLogger
from tests.support.fakes.fake_volumes import FakeVolumesFs

fs = fake_fs_fixture


@pytest.mark.slow
class TestRestoreMalformedRange:
    @pytest.fixture(autouse=True)
    def setup(self, fs):
        self.fixture = RestoreFileFixture('/XDG_DATA_HOME', fs)
        self.user = RestoreUser(
            environ={'XDG_DATA_HOME': '/XDG_DATA_HOME'},
            uid=123,
            file_reader=fs,
            path_read_fs=fs,
            read_fs=fs,
            write_fs=fs,
            listing_fs=fs,
            version='0.0.0',
            volumes=FakeVolumesFs([]),
            top_trash_dir_rules_reader=fs,
            logger=RecordingLogger())

    def test_a_range_with_two_dashes_gives_an_error_instead_of_crashing(self):
        self.fixture.having_a_trashed_file('/foo/bar')

        res = self.user.run_restore(reply='1-2-3', from_dir='/foo')

        assert res.stderr == 'Invalid entry: not an index: 2-3\n'
