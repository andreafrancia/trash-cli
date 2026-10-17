import errno

import pytest

from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.fslib.fs_remove_file2 import FsRemoveFile2


class UnlistableDirFs(FakeFs):
    # a fake fs where one dir cannot be listed, like a private dir of another user
    def listdir(self, path):
        if path == '/trash/dir/sub':
            raise OSError(errno.EACCES, "Permission denied", path)
        return super(UnlistableDirFs, self).listdir(path)

    def shutil_rmtree(self, path):
        raise OSError(errno.EACCES, "Permission denied", '/trash/dir/sub')


class TestFsRemoveFile2:
    def setup_method(self):
        self.fs = FakeFs()
        self.fs.make_file_and_dirs('/trash/dir/sub/file')
        self.remover = FsRemoveFile2(self.fs)

    def test_a_dir_without_write_bits_is_removed(self):
        self.fs.chmod('/trash/dir/sub', 0o500)
        self.fs.chmod('/trash/dir', 0o500)

        self.remover.remove_file2('/trash/dir')

        assert self.fs.ls_aa('/trash') == []

    def test_an_unreadable_dir_is_left_and_the_modes_are_restored(self):
        self.fs.chmod('/trash/dir/sub', 0o000)
        self.fs.chmod('/trash/dir', 0o500)

        with pytest.raises(OSError):
            self.remover.remove_file2('/trash/dir')

        assert self.fs.get_mod('/trash/dir') == 0o500
        assert self.fs.get_mod('/trash/dir/sub') == 0o000

    def test_a_symlinked_dir_outside_is_not_changed(self):
        self.fs.make_file_and_dirs('/elsewhere/ro/file')
        self.fs.chmod('/elsewhere/ro', 0o500)
        self.fs.symlink('/elsewhere/ro', '/trash/dir/link')
        self.fs.chmod('/trash/dir', 0o500)

        self.remover.remove_file2('/trash/dir')

        assert self.fs.ls_aa('/trash') == []
        assert self.fs.get_mod('/elsewhere/ro') == 0o500
        assert self.fs.ls_aa('/elsewhere/ro') == ['file']

    def test_the_modes_are_restored_when_a_dir_cannot_be_listed(self):
        self.fs = UnlistableDirFs()
        self.fs.make_file_and_dirs('/trash/dir/sub/file')
        self.fs.chmod('/trash/dir/sub', 0o700)
        self.fs.chmod('/trash/dir', 0o500)

        with pytest.raises(OSError):
            FsRemoveFile2(self.fs).remove_file2('/trash/dir')

        assert self.fs.get_mod('/trash/dir') == 0o500
