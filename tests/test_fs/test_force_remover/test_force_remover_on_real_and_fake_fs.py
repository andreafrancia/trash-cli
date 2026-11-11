import pytest

from tests.support.put.real_and_fake_env import env, real_and_fake
from trashcli.fslib.force_remover import ForceRemover

env = env  # the fixture, imported from its module


@pytest.fixture(autouse=True)
def trash_dir(env):
    env.fs.mkdirs(env.path('Trash'))


def home_trash(env):
    # ForceRemover only adds permissions inside the home trash
    return {'HOME': env.base, 'XDG_DATA_HOME': env.base}


def remove_path_forcefully(env, path):
    ForceRemover(env.fs, home_trash(env), lambda: 1000).remove_path_forcefully(path)


# ForceRemover is what trash-empty and trash-rm use to delete a trashed
# file or dir for good.
class TestForceRemover:
    @real_and_fake()
    def test_removes_a_file(self, env):
        env.fs.write_file(env.path('Trash/file'), 'a')

        remove_path_forcefully(env, env.path('Trash/file'))

        assert env.fs.path_lexists(env.path('Trash/file')) is False

    @real_and_fake()
    def test_removes_a_dir_with_its_content(self, env):
        env.fs.mkdirs(env.path('Trash/dir/subdir'))
        env.fs.write_file(env.path('Trash/dir/subdir/file'), 'a')

        remove_path_forcefully(env, env.path('Trash/dir'))

        assert env.fs.path_lexists(env.path('Trash/dir')) is False

    @real_and_fake()
    def test_removes_a_symlink_to_a_dir_not_the_dir(self, env):
        env.fs.mkdirs(env.path('Trash/dir'))
        env.fs.write_file(env.path('Trash/dir/file'), 'a')
        env.fs.symlink(env.path('Trash/dir'), env.path('Trash/link'))

        remove_path_forcefully(env, env.path('Trash/link'))

        assert env.fs.path_lexists(env.path('Trash/link')) is False
        assert env.fs.path_lexists(env.path('Trash/dir/file')) is True

    @real_and_fake()
    def test_fails_on_a_missing_path(self, env):
        with pytest.raises(OSError):
            remove_path_forcefully(env, env.path('Trash/missing'))


# https://github.com/andreafrancia/trash-cli/issues/364
# A trashed dir can contain read-only dirs (e.g. the Go module cache): they
# cannot be emptied as they are, so the dirs being removed are made writable.
class TestForceRemoverOnReadOnlyDirs:
    @real_and_fake()
    def test_removes_a_dir_containing_a_read_only_subdir(self, env):
        env.fs.mkdirs(env.path('Trash/dir/subdir'))
        env.fs.write_file(env.path('Trash/dir/subdir/file'), 'a')
        env.fs.chmod(env.path('Trash/dir/subdir'), 0o555)

        remove_path_forcefully(env, env.path('Trash/dir'))

        assert env.fs.path_lexists(env.path('Trash/dir')) is False

    @real_and_fake()
    def test_removes_a_read_only_dir_with_content(self, env):
        env.fs.mkdirs(env.path('Trash/dir/a/b'))
        env.fs.write_file(env.path('Trash/dir/a/b/file'), 'a')
        env.fs.chmod(env.path('Trash/dir/a/b'), 0o555)
        env.fs.chmod(env.path('Trash/dir/a'), 0o555)
        env.fs.chmod(env.path('Trash/dir'), 0o555)

        remove_path_forcefully(env, env.path('Trash/dir'))

        assert env.fs.path_lexists(env.path('Trash/dir')) is False

    @real_and_fake()
    def test_removes_a_dir_with_a_subdir_that_has_no_search_permission(self, env):
        env.fs.mkdirs(env.path('Trash/dir/subdir'))
        env.fs.write_file(env.path('Trash/dir/subdir/file'), 'a')
        env.fs.chmod(env.path('Trash/dir/subdir'), 0o400)

        remove_path_forcefully(env, env.path('Trash/dir'))

        assert env.fs.path_lexists(env.path('Trash/dir')) is False

    @real_and_fake()
    def test_does_not_change_the_permissions_of_a_symlink_target(self, env):
        # a symlink inside the trashed dir can point outside the trash
        env.fs.mkdirs(env.path('Trash/outside'))
        env.fs.chmod(env.path('Trash/outside'), 0o555)
        env.fs.mkdirs(env.path('Trash/dir/subdir'))
        env.fs.symlink(env.path('Trash/outside'), env.path('Trash/dir/subdir/link'))
        env.fs.chmod(env.path('Trash/dir/subdir'), 0o555)

        try:
            remove_path_forcefully(env, env.path('Trash/dir'))

            assert env.fs.path_lexists(env.path('Trash/dir')) is False
            assert env.fs.get_mod(env.path('Trash/outside')) == 0o555
        finally:
            env.fs.chmod(env.path('Trash/outside'), 0o755)

    @real_and_fake()
    def test_does_not_change_the_permissions_of_the_parent(self, env):
        env.fs.mkdirs(env.path('Trash/parent/dir/subdir'))
        env.fs.write_file(env.path('Trash/parent/dir/subdir/file'), 'a')
        env.fs.chmod(env.path('Trash/parent/dir/subdir'), 0o555)
        env.fs.chmod(env.path('Trash/parent'), 0o555)

        try:
            with pytest.raises(OSError):
                remove_path_forcefully(env, env.path('Trash/parent/dir'))

            assert env.fs.get_mod(env.path('Trash/parent')) == 0o555
        finally:
            env.fs.chmod(env.path('Trash/parent'), 0o755)
            env.fs.chmod(env.path('Trash/parent/dir'), 0o755)
            if env.fs.path_lexists(env.path('Trash/parent/dir/subdir')):
                env.fs.chmod(env.path('Trash/parent/dir/subdir'), 0o755)

    @real_and_fake()
    def test_does_not_read_an_unreadable_dir(self, env):
        # only the permissions needed to unlink are added, not the read one
        env.fs.mkdirs(env.path('Trash/dir/subdir'))
        env.fs.write_file(env.path('Trash/dir/subdir/file'), 'a')
        env.fs.chmod(env.path('Trash/dir/subdir'), 0o300)

        try:
            with pytest.raises(OSError):
                remove_path_forcefully(env, env.path('Trash/dir'))

            assert env.fs.path_lexists(env.path('Trash/dir/subdir/file')) is True
        finally:
            env.fs.chmod(env.path('Trash/dir/subdir'), 0o700)

    @real_and_fake()
    def test_leaves_writable_dirs_unchanged_when_it_fails(self, env):
        # the permissions are changed only where it is needed
        env.fs.mkdirs(env.path('Trash/dir/subdir'))
        env.fs.write_file(env.path('Trash/dir/subdir/file'), 'a')
        env.fs.chmod(env.path('Trash/dir/subdir'), 0o300)
        env.fs.chmod(env.path('Trash/dir'), 0o750)

        try:
            with pytest.raises(OSError):
                remove_path_forcefully(env, env.path('Trash/dir'))

            assert env.fs.get_mod(env.path('Trash/dir')) == 0o750
        finally:
            env.fs.chmod(env.path('Trash/dir/subdir'), 0o700)

    @real_and_fake()
    def test_restores_only_the_owner_bits_when_it_fails_BUG(self, env):
        # Characterizes a known bug: the dirs that survive a failure should be
        # left as they were found (0o555), but restore_modes() keeps only the
        # owner bits (keep_only_user_bits), so they lose the group and other
        # bits and end up as 0o500.
        env.fs.mkdirs(env.path('Trash/dir/a/unreadable'))
        env.fs.write_file(env.path('Trash/dir/a/unreadable/file'), 'a')
        env.fs.chmod(env.path('Trash/dir/a/unreadable'), 0o300)
        env.fs.chmod(env.path('Trash/dir/a'), 0o555)
        env.fs.chmod(env.path('Trash/dir'), 0o555)

        try:
            with pytest.raises(OSError):
                remove_path_forcefully(env, env.path('Trash/dir'))

            assert env.fs.get_mod(env.path('Trash/dir')) == 0o500  # should be 0o555
            assert env.fs.get_mod(env.path('Trash/dir/a')) == 0o500  # should be 0o555
            assert env.fs.get_mod(env.path('Trash/dir/a/unreadable')) == 0o300
        finally:
            env.fs.chmod(env.path('Trash/dir'), 0o755)
            env.fs.chmod(env.path('Trash/dir/a'), 0o755)
            env.fs.chmod(env.path('Trash/dir/a/unreadable'), 0o755)

    @real_and_fake()
    def test_root_never_self_heals(self, env):
        # root is not stopped by mode bits, so it must not chmod other
        # users' files either: it never attempts the self-heal at all.
        env.fs.mkdirs(env.path('Trash/dir/subdir'))
        env.fs.write_file(env.path('Trash/dir/subdir/file'), 'a')
        env.fs.chmod(env.path('Trash/dir/subdir'), 0o500)
        env.fs.chmod(env.path('Trash/dir'), 0o500)

        try:
            with pytest.raises(OSError):
                ForceRemover(env.fs, home_trash(env), lambda: 0
                            ).remove_path_forcefully(env.path('Trash/dir'))

            assert env.fs.get_mod(env.path('Trash/dir')) == 0o500
            assert env.fs.get_mod(env.path('Trash/dir/subdir')) == 0o500
        finally:
            env.fs.chmod(env.path('Trash/dir'), 0o700)
            env.fs.chmod(env.path('Trash/dir/subdir'), 0o700)

    @real_and_fake()
    def test_a_path_outside_the_home_trash_never_self_heals(self, env):
        env.fs.mkdirs(env.path('outside/dir/subdir'))
        env.fs.write_file(env.path('outside/dir/subdir/file'), 'a')
        env.fs.chmod(env.path('outside/dir/subdir'), 0o500)
        env.fs.chmod(env.path('outside/dir'), 0o500)

        try:
            with pytest.raises(OSError):
                remove_path_forcefully(env, env.path('outside/dir'))

            assert env.fs.get_mod(env.path('outside/dir')) == 0o500
            assert env.fs.get_mod(env.path('outside/dir/subdir')) == 0o500
        finally:
            env.fs.chmod(env.path('outside/dir'), 0o700)
            env.fs.chmod(env.path('outside/dir/subdir'), 0o700)
