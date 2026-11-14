import errno

import pytest

from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.fslib.force_remover import ForceRemover


HOME_TRASH = {'HOME': '/xdg', 'XDG_DATA_HOME': '/xdg'}


def make_dir_unlistable(fs, unlistable):
    # like a private dir of another user: it cannot be listed or removed
    listdir = fs.listdir

    def listdir_except_unlistable(path):
        if path == unlistable:
            raise OSError(errno.EACCES, "Permission denied", path)
        return listdir(path)

    def rmtree_stopped_by_unlistable(path):
        raise OSError(errno.EACCES, "Permission denied", unlistable)

    fs.listdir = listdir_except_unlistable
    fs.shutil_rmtree = rmtree_stopped_by_unlistable


class TestForceRemoverOnFakeFs:
    def setup_method(self):
        self.fs = FakeFs()
        self.fs.make_file_and_dirs('/xdg/Trash/dir/sub/file')
        # a fixed non-root uid keeps the result independent of the test runner
        self.remover = ForceRemover(self.fs, HOME_TRASH, lambda: 1000)

    def test_a_dir_without_write_bits_is_removed(self):
        self.fs.chmod('/xdg/Trash/dir/sub', 0o500)
        self.fs.chmod('/xdg/Trash/dir', 0o500)

        self.remover.remove_path_forcefully('/xdg/Trash/dir')

        assert self.fs.ls_aa('/xdg/Trash') == []

    def test_an_unreadable_dir_is_left_and_the_modes_are_restored(self):
        self.fs.chmod('/xdg/Trash/dir/sub', 0o000)
        self.fs.chmod('/xdg/Trash/dir', 0o500)

        with pytest.raises(OSError):
            self.remover.remove_path_forcefully('/xdg/Trash/dir')

        assert self.fs.get_mod('/xdg/Trash/dir') == 0o500
        assert self.fs.get_mod('/xdg/Trash/dir/sub') == 0o000

    def test_a_symlinked_dir_outside_is_not_changed(self):
        self.fs.make_file_and_dirs('/elsewhere/ro/file')
        self.fs.chmod('/elsewhere/ro', 0o500)
        self.fs.symlink('/elsewhere/ro', '/xdg/Trash/dir/link')
        self.fs.chmod('/xdg/Trash/dir', 0o500)

        self.remover.remove_path_forcefully('/xdg/Trash/dir')

        assert self.fs.ls_aa('/xdg/Trash') == []
        assert self.fs.get_mod('/elsewhere/ro') == 0o500
        assert self.fs.ls_aa('/elsewhere/ro') == ['file']

    def test_the_modes_are_restored_when_a_dir_cannot_be_listed(self):
        make_dir_unlistable(self.fs, '/xdg/Trash/dir/sub')
        self.fs.chmod('/xdg/Trash/dir/sub', 0o700)
        self.fs.chmod('/xdg/Trash/dir', 0o500)

        with pytest.raises(OSError):
            self.remover.remove_path_forcefully('/xdg/Trash/dir')

        assert self.fs.get_mod('/xdg/Trash/dir') == 0o500

    def test_root_does_not_change_any_mode(self):
        self.fs.chmod('/xdg/Trash/dir/sub', 0o500)
        self.fs.chmod('/xdg/Trash/dir', 0o500)

        with pytest.raises(OSError):
            ForceRemover(self.fs, HOME_TRASH, lambda: 0).remove_path_forcefully('/xdg/Trash/dir')

        assert self.fs.get_mod('/xdg/Trash/dir') == 0o500

    def test_a_dir_outside_the_home_trash_is_not_changed(self):
        self.fs.make_file_and_dirs('/outside/dir/sub/file')
        self.fs.chmod('/outside/dir', 0o500)

        with pytest.raises(OSError):
            self.remover.remove_path_forcefully('/outside/dir')

        assert self.fs.get_mod('/outside/dir') == 0o500

    def test_only_owner_bits_are_added(self):
        self.fs.chmod('/xdg/Trash/dir/sub', 0o2557)
        self.fs.chmod('/xdg/Trash/dir', 0o2557)
        modes = []
        chmod = self.fs.chmod
        self.fs.chmod = lambda path, mode: modes.append(mode) or chmod(path, mode)

        self.remover.remove_path_forcefully('/xdg/Trash/dir')

        # no group, other or special bit is added to a trashed dir
        assert modes and all(m & ~0o700 == 0 for m in modes)

    def test_a_symlinked_dir_is_not_descended(self):
        self.fs.make_file_and_dirs('/elsewhere/outer/inner/file')
        self.fs.chmod('/elsewhere/outer/inner', 0o500)
        self.fs.symlink('/elsewhere/outer', '/xdg/Trash/dir/link')
        self.fs.chmod('/xdg/Trash/dir', 0o500)

        self.remover.remove_path_forcefully('/xdg/Trash/dir')

        assert self.fs.get_mod('/elsewhere/outer/inner') == 0o500

    def test_a_dir_owned_by_another_user_is_not_chmoded(self):
        # chmod fails with EPERM, as it would on a real fs for a dir we
        # don't own: only the owner (or root) can change its mode.
        self.fs.chmod('/xdg/Trash/dir/sub', 0o500)
        self.fs.chmod('/xdg/Trash/dir', 0o500)
        self.fs.chown_to_another_user('/xdg/Trash/dir')

        with pytest.raises(OSError):
            self.remover.remove_path_forcefully('/xdg/Trash/dir')

        assert self.fs.get_mod('/xdg/Trash/dir') == 0o500
        assert self.fs.get_mod('/xdg/Trash/dir/sub') == 0o500
