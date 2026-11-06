import pytest

from tests.support.put.real_and_fake_env import env, real_and_fake
from trashcli.fslib.fs_remove_file2 import FsRemoveFile2

env = env  # the fixture, imported from its module


def remove_file2(env, path):
    FsRemoveFile2(env.fs).remove_file2(path)


# FsRemoveFile2 is what trash-empty and trash-rm use to delete a trashed
# file or dir for good.
class TestFsRemoveFile2:
    @real_and_fake()
    def test_removes_a_file(self, env):
        env.fs.write_file(env.path('file'), 'a')

        remove_file2(env, env.path('file'))

        assert env.fs.path_lexists(env.path('file')) is False

    @real_and_fake()
    def test_removes_a_dir_with_its_content(self, env):
        env.fs.mkdirs(env.path('dir/subdir'))
        env.fs.write_file(env.path('dir/subdir/file'), 'a')

        remove_file2(env, env.path('dir'))

        assert env.fs.path_lexists(env.path('dir')) is False

    @real_and_fake()
    def test_removes_a_symlink_to_a_dir_not_the_dir(self, env):
        env.fs.mkdirs(env.path('dir'))
        env.fs.write_file(env.path('dir/file'), 'a')
        env.fs.symlink(env.path('dir'), env.path('link'))

        remove_file2(env, env.path('link'))

        assert env.fs.path_lexists(env.path('link')) is False
        assert env.fs.path_lexists(env.path('dir/file')) is True

    @real_and_fake()
    def test_fails_on_a_missing_path(self, env):
        with pytest.raises(OSError):
            remove_file2(env, env.path('missing'))


# https://github.com/andreafrancia/trash-cli/issues/364
# A trashed dir can contain read-only dirs (e.g. the Go module cache): they
# cannot be emptied as they are, so the dirs being removed are made writable.
class TestFsRemoveFile2OnReadOnlyDirs:
    @real_and_fake()
    def test_removes_a_dir_containing_a_read_only_subdir(self, env):
        env.fs.mkdirs(env.path('dir/subdir'))
        env.fs.write_file(env.path('dir/subdir/file'), 'a')
        env.fs.chmod(env.path('dir/subdir'), 0o555)

        remove_file2(env, env.path('dir'))

        assert env.fs.path_lexists(env.path('dir')) is False

    @real_and_fake()
    def test_removes_a_read_only_dir_with_content(self, env):
        env.fs.mkdirs(env.path('dir/a/b'))
        env.fs.write_file(env.path('dir/a/b/file'), 'a')
        env.fs.chmod(env.path('dir/a/b'), 0o555)
        env.fs.chmod(env.path('dir/a'), 0o555)
        env.fs.chmod(env.path('dir'), 0o555)

        remove_file2(env, env.path('dir'))

        assert env.fs.path_lexists(env.path('dir')) is False

    @real_and_fake()
    def test_removes_a_dir_with_a_subdir_that_has_no_search_permission(self, env):
        env.fs.mkdirs(env.path('dir/subdir'))
        env.fs.write_file(env.path('dir/subdir/file'), 'a')
        env.fs.chmod(env.path('dir/subdir'), 0o400)

        remove_file2(env, env.path('dir'))

        assert env.fs.path_lexists(env.path('dir')) is False

    @real_and_fake()
    def test_does_not_change_the_permissions_of_a_symlink_target(self, env):
        # a symlink inside the trashed dir can point outside the trash
        env.fs.mkdirs(env.path('outside'))
        env.fs.chmod(env.path('outside'), 0o555)
        env.fs.mkdirs(env.path('dir/subdir'))
        env.fs.symlink(env.path('outside'), env.path('dir/subdir/link'))
        env.fs.chmod(env.path('dir/subdir'), 0o555)

        try:
            remove_file2(env, env.path('dir'))

            assert env.fs.path_lexists(env.path('dir')) is False
            assert env.fs.get_mod(env.path('outside')) == 0o555
        finally:
            env.fs.chmod(env.path('outside'), 0o755)

    @real_and_fake()
    def test_does_not_change_the_permissions_of_the_parent(self, env):
        env.fs.mkdirs(env.path('parent/dir/subdir'))
        env.fs.write_file(env.path('parent/dir/subdir/file'), 'a')
        env.fs.chmod(env.path('parent/dir/subdir'), 0o555)
        env.fs.chmod(env.path('parent'), 0o555)

        try:
            with pytest.raises(OSError):
                remove_file2(env, env.path('parent/dir'))

            assert env.fs.get_mod(env.path('parent')) == 0o555
        finally:
            env.fs.chmod(env.path('parent'), 0o755)
            env.fs.chmod(env.path('parent/dir'), 0o755)
            if env.fs.path_lexists(env.path('parent/dir/subdir')):
                env.fs.chmod(env.path('parent/dir/subdir'), 0o755)

    @real_and_fake()
    def test_does_not_read_an_unreadable_dir(self, env):
        # only the permissions needed to unlink are added, not the read one
        env.fs.mkdirs(env.path('dir/subdir'))
        env.fs.write_file(env.path('dir/subdir/file'), 'a')
        env.fs.chmod(env.path('dir/subdir'), 0o300)

        try:
            with pytest.raises(OSError):
                remove_file2(env, env.path('dir'))

            assert env.fs.path_lexists(env.path('dir/subdir/file')) is True
        finally:
            env.fs.chmod(env.path('dir/subdir'), 0o700)

    @real_and_fake()
    def test_leaves_writable_dirs_unchanged_when_it_fails(self, env):
        # the permissions are changed only where it is needed
        env.fs.mkdirs(env.path('dir/subdir'))
        env.fs.write_file(env.path('dir/subdir/file'), 'a')
        env.fs.chmod(env.path('dir/subdir'), 0o300)
        env.fs.chmod(env.path('dir'), 0o750)

        try:
            with pytest.raises(OSError):
                remove_file2(env, env.path('dir'))

            assert env.fs.get_mod(env.path('dir')) == 0o750
        finally:
            env.fs.chmod(env.path('dir/subdir'), 0o700)
