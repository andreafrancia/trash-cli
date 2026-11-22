from typing import TypeVar

import pytest

from tests.support.dirs.my_path import MyPath
from tests.support.fs_fixture import real_fs_fixture
from tests.support.restore.restore_user import RestoreUser
from tests.support.dirs.support_fs import SupportFs
from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.support.fakes.fake_trash_dir import FakeTrashDir
from tests.support.py2mock import Mock
from tests.test_restore.support.recording_logger import RecordingLogger
from tests.support.fakes.fake_volumes import FakeVolumesFs
from trashcli.fslib.protocols.fs import Fs
from trashcli.restore.trashed_files import TrashedFiles

Self = TypeVar('Self', bound='TestTrashedFileRestoreIntegration')

fs = real_fs_fixture
temp_dir = temp_dir_fixture

@pytest.mark.slow
class TestTrashedFileRestoreIntegration:

    @pytest.fixture(autouse=True)
    def setup(self,
              fs,  # type: Fs
              temp_dir,  # type: MyPath
              ):
        self.temp_dir = temp_dir
        self.root_dir = self.temp_dir
        self.support_fs = SupportFs(fs, self.root_dir)
        self.home_dir = self.root_dir / "home/user"
        self.trash_dir_path = self.home_dir / ".local/share/Trash"
        self.cwd = self.root_dir / "cwd"

        self.support_fs.mkdir_rel_p(self.cwd)
        self.support_fs.mkdir_rel_p(self.home_dir)

        self.trash_dir = FakeTrashDir(self.trash_dir_path, fs)

        self.logger = RecordingLogger()
        self.trashed_files = Mock(spec=TrashedFiles)
        self.user = RestoreUser(
            environ={'HOME': self.home_dir},
            uid=1000,
            fs=fs,
            version="0.0.0.",
            volumes=FakeVolumesFs([]),
            logger=self.logger,
        )

    def test_restore_one_file(self,  # type: Self
                              ):
        self.trash_dir.add_file_trashed_from_dir('foo-bar', self.cwd)
        assert sorted(self.support_fs.find_files_rel()) == [
            '/home/user/.local/share/Trash/files/foo-bar',
            '/home/user/.local/share/Trash/info/foo-bar.trashinfo',
        ]

        r = self.user.run_restore(['trash-restore'], reply="0", from_dir=self.cwd)

        assert r.stderr == ''
        files_after_restore = sorted(self.support_fs.find_files_rel())
        assert (files_after_restore == ['/cwd/foo-bar'])
        assert '/home/user/.local/share/Trash/info/foo-bar.trashinfo' not in files_after_restore
        assert '/home/user/.local/share/Trash/files/foo-bar' not in files_after_restore

    def test_restore_file_with_parent(self,  # type: Self
                                      ):
        self.trash_dir.add_file_trashed_from_dir('foo', self.cwd / 'parent')
        assert sorted(self.support_fs.find_files_rel()) == [
            '/home/user/.local/share/Trash/files/foo',
            '/home/user/.local/share/Trash/info/foo.trashinfo',
        ]

        self.user.run_restore(['trash-restore'], reply="0", from_dir=self.cwd)

        # assert it has been restored
        assert self.support_fs.exists('/cwd/parent/foo')
        # assert that trashinfo is gone
        assert not self.support_fs.exists(
            '/home/user/.local/share/Trash/info/foo.trashinfo')
        # assert that backup copy is no there
        assert not self.support_fs.exists(
            '/home/user/.local/share/Trash/files/foo')
        # assert noting more to check in root_dir
        assert sorted(self.support_fs.find_files_rel()) == ['/cwd/parent/foo']
        # assert no warnings
        assert self.logger.captured == []

    def test_restore_over_existing_file_will_obstruct_restoration(self,
                                                                  # type: Self
                                                                  ):
        """
        What happens when we cannot restore file because another file is the
        restore location.
        """
        self.trash_dir.add_file_trashed_from_dir('bar', self.cwd,
                                                 'to-be-restored')
        self.support_fs.write_file('cwd/bar',
                                   'obstructing file')  # put a file where the trashed one should be restored
        assert sorted(self.support_fs.find_files_rel()) == [
            '/cwd/bar',
            '/home/user/.local/share/Trash/files/bar',
            '/home/user/.local/share/Trash/info/bar.trashinfo',
        ]

        r = self.user.run_restore(['trash-restore'], reply="0", from_dir=self.cwd)

        assert sorted(self.support_fs.find_files_rel()) == [
            '/cwd/bar',
            '/home/user/.local/share/Trash/files/bar',
            '/home/user/.local/share/Trash/info/bar.trashinfo',
        ]

        # assert it cannot be restored
        assert self.support_fs.read('cwd/bar') != 'to-be-restored'
        assert self.support_fs.read('cwd/bar') == 'obstructing file'
        # assert that trashinfo remains there
        assert self.support_fs.exists(
            '/home/user/.local/share/Trash/info/bar.trashinfo')
        # assert that backup copy remains there
        assert self.support_fs.exists('/home/user/.local/share/Trash/files/bar')
        # assert a warning is passed
        assert r.stderr == 'Refusing to overwrite existing file "bar".\n'
        assert r.exit_code == 1
