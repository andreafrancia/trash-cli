import errno

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
