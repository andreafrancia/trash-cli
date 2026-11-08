import errno
import os

import pytest

from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.fslib.fs_remove_file2 import FsRemoveFile2


class UnlistableDirFs(FakeFs):
    # a fake fs where one dir cannot be listed, like a private dir of another user
    def listdir(self, path):
        if path == '/xdg/Trash/dir/sub':
            raise OSError(errno.EACCES, "Permission denied", path)
        return super(UnlistableDirFs, self).listdir(path)

    def shutil_rmtree(self, path):
        raise OSError(errno.EACCES, "Permission denied", '/xdg/Trash/dir/sub')


class TestFsRemoveFile2:
    @pytest.fixture(autouse=True)
    def home_trash(self, monkeypatch):
        monkeypatch.setenv('HOME', '/xdg')
        monkeypatch.setenv('XDG_DATA_HOME', '/xdg')
        # a fixed non-root uid keeps the result independent of the test runner
        monkeypatch.setattr(os, 'geteuid', lambda: 1000)

    def setup_method(self):
        self.fs = FakeFs()
        self.fs.make_file_and_dirs('/xdg/Trash/dir/sub/file')
        self.remover = FsRemoveFile2(self.fs)

    def test_a_dir_without_write_bits_is_removed(self):
        self.fs.chmod('/xdg/Trash/dir/sub', 0o500)
        self.fs.chmod('/xdg/Trash/dir', 0o500)

        self.remover.remove_file2('/xdg/Trash/dir')

        assert self.fs.ls_aa('/xdg/Trash') == []

    def test_an_unreadable_dir_is_left_and_the_modes_are_restored(self):
        self.fs.chmod('/xdg/Trash/dir/sub', 0o000)
        self.fs.chmod('/xdg/Trash/dir', 0o500)

        with pytest.raises(OSError):
            self.remover.remove_file2('/xdg/Trash/dir')

        assert self.fs.get_mod('/xdg/Trash/dir') == 0o500
        assert self.fs.get_mod('/xdg/Trash/dir/sub') == 0o000

    def test_a_symlinked_dir_outside_is_not_changed(self):
        self.fs.make_file_and_dirs('/elsewhere/ro/file')
        self.fs.chmod('/elsewhere/ro', 0o500)
        self.fs.symlink('/elsewhere/ro', '/xdg/Trash/dir/link')
        self.fs.chmod('/xdg/Trash/dir', 0o500)

        self.remover.remove_file2('/xdg/Trash/dir')

        assert self.fs.ls_aa('/xdg/Trash') == []
        assert self.fs.get_mod('/elsewhere/ro') == 0o500
        assert self.fs.ls_aa('/elsewhere/ro') == ['file']

    def test_the_modes_are_restored_when_a_dir_cannot_be_listed(self):
        self.fs = UnlistableDirFs()
        self.fs.make_file_and_dirs('/xdg/Trash/dir/sub/file')
        self.fs.chmod('/xdg/Trash/dir/sub', 0o700)
        self.fs.chmod('/xdg/Trash/dir', 0o500)

        with pytest.raises(OSError):
            FsRemoveFile2(self.fs).remove_file2('/xdg/Trash/dir')

        assert self.fs.get_mod('/xdg/Trash/dir') == 0o500

    def test_root_does_not_change_any_mode(self, monkeypatch):
        monkeypatch.setattr(os, 'geteuid', lambda: 0)
        self.fs.chmod('/xdg/Trash/dir/sub', 0o500)
        self.fs.chmod('/xdg/Trash/dir', 0o500)

        with pytest.raises(OSError):
            self.remover.remove_file2('/xdg/Trash/dir')

        assert self.fs.get_mod('/xdg/Trash/dir') == 0o500

    def test_a_dir_outside_the_home_trash_is_not_changed(self):
        self.fs.make_file_and_dirs('/outside/dir/sub/file')
        self.fs.chmod('/outside/dir', 0o500)

        with pytest.raises(OSError):
            self.remover.remove_file2('/outside/dir')

        assert self.fs.get_mod('/outside/dir') == 0o500

    def test_only_owner_bits_are_added(self, monkeypatch):
        modes = []
        base_chmod = FakeFs.chmod
        monkeypatch.setattr(FakeFs, 'chmod',
                            lambda fs, p, m: modes.append(m) or base_chmod(fs, p, m))
        self.fs.chmod('/xdg/Trash/dir/sub', 0o2557)
        self.fs.chmod('/xdg/Trash/dir', 0o2557)
        del modes[:]  # keep only the modes set while removing

        self.remover.remove_file2('/xdg/Trash/dir')

        # no group, other or special bit is added to a trashed dir
        assert modes and all(m & ~0o700 == 0 for m in modes)

    def test_a_symlinked_dir_is_not_descended(self):
        self.fs.make_file_and_dirs('/elsewhere/outer/inner/file')
        self.fs.chmod('/elsewhere/outer/inner', 0o500)
        self.fs.symlink('/elsewhere/outer', '/xdg/Trash/dir/link')
        self.fs.chmod('/xdg/Trash/dir', 0o500)

        self.remover.remove_file2('/xdg/Trash/dir')

        assert self.fs.get_mod('/elsewhere/outer/inner') == 0o500
