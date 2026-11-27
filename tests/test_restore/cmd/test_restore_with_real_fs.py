import pytest

from tests.support.asserts.assert_that import assert_that
from tests.support.dirs.my_path import MyPath
from tests.support.dirs.temp_dir import make_temp_dir, temp_dir_fixture
from tests.support.fs_fixture import real_fs_fixture
from tests.support.restore.a_trashed_file import ATrashedFile
from tests.support.restore.has_been_restored_matcher import \
    has_been_restored
from tests.support.restore.restore_file_fixture import RestoreFileFixture
from tests.support.restore.restore_user import RestoreUser
from tests.test_restore.support.recording_logger import RecordingLogger
from tests.support.fakes.fake_volumes import FakeVolumesFs
from trashcli.fslib.protocols.fs import Fs

fs = real_fs_fixture
temp_dir = temp_dir_fixture

@pytest.mark.slow
class TestRestoreTrash:
    @pytest.fixture(autouse=True)
    def setup(self,
              fs,  # type: Fs
              temp_dir,  # type: MyPath
              ):
        self.fixture = RestoreFileFixture(temp_dir / 'XDG_DATA_HOME',
                                          fs)
        self.cwd = temp_dir / "cwd"
        XDG_DATA_HOME = temp_dir / 'XDG_DATA_HOME'
        self.trash_dir = XDG_DATA_HOME / 'Trash'
        self.user = RestoreUser(environ={'XDG_DATA_HOME': XDG_DATA_HOME},
                                uid=123,
                                fs=fs,
                                version='0.0.0',
                                volumes=FakeVolumesFs([]),
                                logger=RecordingLogger())

    def test_it_does_nothing_when_no_file_have_been_found_in_current_dir(self):
        res = self.user.run_restore(from_dir='/')

        assert res.output() == "No files trashed from current dir ('/')\n"

    def test_gives_an_error_on_not_a_number_input(self):
        self.fixture.having_a_trashed_file('/foo/bar')

        res = self.user.run_restore(reply='+@notanumber', from_dir='/foo')

        assert res.stderr == 'Invalid entry: not an index: +@notanumber\n'

    def test_it_gives_error_when_user_input_is_too_small(self):
        self.fixture.having_a_trashed_file('/foo/bar')

        res = self.user.run_restore(reply='1', from_dir='/foo')

        assert res.stderr == 'Invalid entry: out of range 0..0: 1\n'

    def test_it_gives_error_when_user_input_is_too_large(self):
        self.fixture.having_a_trashed_file('/foo/bar')

        res = self.user.run_restore(reply='1', from_dir='/foo')

        assert res.stderr == 'Invalid entry: out of range 0..0: 1\n'

    def test_it_shows_the_file_deleted_from_the_current_dir(self):
        self.fixture.having_a_trashed_file('/foo/bar')

        res = self.user.run_restore(reply='', from_dir='/foo')

        assert res.output() == ('   0 2000-01-01 00:00:01 /foo/bar\n'
                                'No files were restored\n')
        assert res.stderr == ''

    def test_it_restores_the_file_selected_by_the_user(self):
        self.fixture.having_a_trashed_file(self.cwd / 'foo')

        self.user.run_restore(reply='0', from_dir=self.cwd)

        self.fixture.file_should_have_been_restored(self.cwd / 'foo')

    def test_it_refuses_overwriting_existing_file(self):
        self.fixture.having_a_trashed_file(self.cwd / 'foo')
        self.fixture.make_file(self.cwd / "foo")

        res = self.user.run_restore(reply='0', from_dir=self.cwd)

        assert res.stderr == 'Refusing to overwrite existing file "foo".\n'

    def test_it_restores_the_file_and_delete_the_trash_info(
            self, fs
    ):
        a_trashed_file = self.make_trashed_file()

        res = self.user.run_restore(reply='0', from_dir=self.cwd)

        assert res.stderr == ''
        assert_that(a_trashed_file, has_been_restored(fs))

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
