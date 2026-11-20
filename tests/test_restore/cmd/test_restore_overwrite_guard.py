import pytest

from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.support.fakes.fake_trash_dir import trashinfo_content_default_date
from tests.support.fs_fixture import real_fs_fixture
from tests.support.restore.restore_file_fixture import RestoreFileFixture
from tests.support.restore.restore_user import RestoreUser
from tests.test_restore.support.recording_logger import RecordingLogger
from tests.support.fakes.fake_volumes import FakeVolumesFs


fs = real_fs_fixture
temp_dir = temp_dir_fixture

@pytest.mark.slow
class TestRestoreOverwriteGuard:
    @pytest.fixture(autouse=True)
    def setup(self, fs, temp_dir):
        self.fixture = RestoreFileFixture(temp_dir / 'XDG_DATA_HOME',
                                          fs)
        self.cwd = temp_dir / 'cwd'
        fs.makedirs(self.cwd)
        self.user = RestoreUser(
            environ={'XDG_DATA_HOME': temp_dir / 'XDG_DATA_HOME'},
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

    def test_it_refuses_to_restore_over_a_dangling_symlink(
            self, fs):
        self.fixture.having_a_trashed_file(self.cwd / 'foo')
        fs.symlink(self.cwd / 'this-target-does-not-exist', self.cwd / 'foo')

        res = self.user.run_restore(reply='0', from_dir=self.cwd)

        assert res.stderr == 'Refusing to overwrite existing file "foo".\n'

    def test_it_refuses_to_restore_onto_a_directory_even_with_overwrite(
            self, fs
    ):
        self.fixture.having_a_trashed_file(self.cwd / 'foo')
        fs.makedirs(self.cwd / 'foo')

        res = self.user.run_restore(args=['trash-restore', '--overwrite'],
                                    reply='0', from_dir=self.cwd)

        assert res.stderr == 'Refusing to overwrite existing file "foo".\n'

    def test_batch_keeps_conflicting_entry_and_restores_the_next_file(
            self, fs, temp_dir):
        trash = temp_dir / 'XDG_DATA_HOME/Trash'
        for name in ['a', 'b']:
            self.fixture.make_file(trash / ('info/' + name + '.trashinfo'),
                                   trashinfo_content_default_date(self.cwd / name))
            self.fixture.make_file(trash / ('files/' + name), 'trashed ' + name)
        self.fixture.make_file(self.cwd / 'a', 'existing a')

        res = self.user.run_restore(args=['trash-restore', '--sort=path'],
                                    reply='0-1', from_dir=self.cwd)

        assert res.exit_code == 1
        assert res.stderr == 'Refusing to overwrite existing file "a".\n'
        assert fs.read_file(self.cwd / 'a') == 'existing a'
        assert fs.read_file(self.cwd / 'b') == 'trashed b'
        assert fs.read_file(trash / 'files/a') == 'trashed a'
        assert fs.path_exists(trash / 'info/a.trashinfo')
        assert not fs.path_exists(trash / 'files/b')
        assert not fs.path_exists(trash / 'info/b.trashinfo')
