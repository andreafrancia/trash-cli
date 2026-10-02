import errno

import pytest

from tests.support.put.real_and_fake_env import env, real_and_fake

env = env  # the fixture, imported from its module


# Characterization of RealFs.shutil_rmtree (shutil.rmtree): FakeFs has to
# behave the same way.
class TestShutilRmtreeLikeRealFs:
    @real_and_fake()
    def test_removes_an_empty_dir(self, env):
        env.fs.mkdir(env.path('dir'))

        env.fs.shutil_rmtree(env.path('dir'))

        assert env.fs.path_lexists(env.path('dir')) is False

    @real_and_fake()
    def test_removes_a_dir_with_its_content(self, env):
        env.fs.mkdirs(env.path('dir/subdir'))
        env.fs.write_file(env.path('dir/a'), 'a')
        env.fs.write_file(env.path('dir/subdir/b'), 'b')

        env.fs.shutil_rmtree(env.path('dir'))

        assert env.fs.path_lexists(env.path('dir')) is False

    @real_and_fake()
    def test_removes_the_symlinks_inside_not_their_targets(self, env):
        env.fs.write_file(env.path('target'), 'a')
        env.fs.mkdir(env.path('dir'))
        env.fs.symlink(env.path('target'), env.path('dir/link'))

        env.fs.shutil_rmtree(env.path('dir'))

        assert env.fs.path_lexists(env.path('dir')) is False
        assert env.fs.path_lexists(env.path('target')) is True

    @real_and_fake()
    def test_fails_on_a_missing_path(self, env):
        with pytest.raises(OSError) as excinfo:
            env.fs.shutil_rmtree(env.path('missing'))

        assert excinfo.value.errno == errno.ENOENT

    @real_and_fake()
    def test_fails_on_a_file_and_leaves_it(self, env):
        env.fs.write_file(env.path('file'), 'a')

        with pytest.raises(OSError):
            env.fs.shutil_rmtree(env.path('file'))

        assert env.fs.path_lexists(env.path('file')) is True

    @real_and_fake()
    def test_fails_on_a_symlink_to_a_dir_and_leaves_both(self, env):
        env.fs.mkdir(env.path('dir'))
        env.fs.symlink(env.path('dir'), env.path('link'))

        with pytest.raises(OSError):
            env.fs.shutil_rmtree(env.path('link'))

        assert env.fs.path_lexists(env.path('link')) is True
        assert env.fs.path_isdir(env.path('dir')) is True

    @real_and_fake()
    def test_does_not_touch_the_other_entries(self, env):
        env.fs.mkdir(env.path('a'))
        env.fs.mkdir(env.path('b'))

        env.fs.shutil_rmtree(env.path('a'))

        assert sorted(env.fs.listdir(env.base)) == ['b']

    @real_and_fake()
    def test_fails_on_an_unreadable_dir_and_leaves_it(self, env):
        env.fs.mkdir(env.path('dir'))
        env.fs.chmod(env.path('dir'), 0o300)

        try:
            with pytest.raises(OSError) as excinfo:
                env.fs.shutil_rmtree(env.path('dir'))

            assert excinfo.value.errno == errno.EACCES
            assert env.fs.path_lexists(env.path('dir')) is True
        finally:
            env.fs.chmod(env.path('dir'), 0o700)


# The failure cases with permissions. To remove a dir with its content:
#  - every dir of the tree has to be readable (to list it);
#  - a dir with entries needs write and search permissions (to unlink them);
#  - the parent of the top dir needs write and search permissions (to rmdir it).
class TestShutilRmtreePermissionsLikeRealFs:
    @real_and_fake()
    def test_fails_when_the_dir_is_not_writable(self, env):
        # the dir can be listed, but its entries cannot be unlinked
        env.fs.mkdir(env.path('dir'))
        env.fs.write_file(env.path('dir/file'), 'a')
        env.fs.chmod(env.path('dir'), 0o500)

        try:
            with pytest.raises(OSError) as excinfo:
                env.fs.shutil_rmtree(env.path('dir'))

            assert excinfo.value.errno == errno.EACCES
            assert env.fs.path_lexists(env.path('dir/file')) is True
        finally:
            env.fs.chmod(env.path('dir'), 0o700)

    @real_and_fake()
    def test_fails_when_the_dir_is_not_searchable(self, env):
        env.fs.mkdir(env.path('dir'))
        env.fs.write_file(env.path('dir/file'), 'a')
        env.fs.chmod(env.path('dir'), 0o600)

        try:
            with pytest.raises(OSError) as excinfo:
                env.fs.shutil_rmtree(env.path('dir'))

            assert excinfo.value.errno == errno.EACCES
        finally:
            env.fs.chmod(env.path('dir'), 0o700)
        assert env.fs.path_lexists(env.path('dir/file')) is True

    @real_and_fake()
    def test_fails_when_a_subdir_is_not_writable(self, env):
        # the top dir can be removed, the file inside the subdir cannot
        env.fs.mkdirs(env.path('dir/subdir'))
        env.fs.write_file(env.path('dir/subdir/file'), 'a')
        env.fs.chmod(env.path('dir/subdir'), 0o500)

        try:
            with pytest.raises(OSError) as excinfo:
                env.fs.shutil_rmtree(env.path('dir'))

            assert excinfo.value.errno == errno.EACCES
            assert env.fs.path_lexists(env.path('dir/subdir/file')) is True
            assert env.fs.path_lexists(env.path('dir')) is True
        finally:
            env.fs.chmod(env.path('dir/subdir'), 0o700)

    @real_and_fake()
    def test_fails_when_a_subdir_is_not_readable(self, env):
        env.fs.mkdirs(env.path('dir/subdir'))
        env.fs.write_file(env.path('dir/subdir/file'), 'a')
        env.fs.chmod(env.path('dir/subdir'), 0o300)

        try:
            with pytest.raises(OSError) as excinfo:
                env.fs.shutil_rmtree(env.path('dir'))

            assert excinfo.value.errno == errno.EACCES
            assert env.fs.path_lexists(env.path('dir/subdir/file')) is True
            assert env.fs.path_lexists(env.path('dir')) is True
        finally:
            env.fs.chmod(env.path('dir/subdir'), 0o700)

    @real_and_fake()
    def test_fails_when_a_subdir_is_not_readable_and_empty(self, env):
        env.fs.mkdirs(env.path('dir/subdir'))
        env.fs.chmod(env.path('dir/subdir'), 0o300)

        try:
            with pytest.raises(OSError) as excinfo:
                env.fs.shutil_rmtree(env.path('dir'))

            assert excinfo.value.errno == errno.EACCES
            assert env.fs.path_lexists(env.path('dir/subdir')) is True
        finally:
            env.fs.chmod(env.path('dir/subdir'), 0o700)

    @real_and_fake()
    def test_fails_when_the_parent_is_not_writable(self, env):
        env.fs.mkdirs(env.path('parent/dir'))
        env.fs.chmod(env.path('parent'), 0o500)

        try:
            with pytest.raises(OSError) as excinfo:
                env.fs.shutil_rmtree(env.path('parent/dir'))

            assert excinfo.value.errno == errno.EACCES
            assert env.fs.path_lexists(env.path('parent/dir')) is True
        finally:
            env.fs.chmod(env.path('parent'), 0o700)

    @real_and_fake()
    def test_an_empty_dir_that_is_not_writable_can_be_removed(self, env):
        # nothing to unlink inside: only the parent's permissions matter
        env.fs.mkdir(env.path('dir'))
        env.fs.chmod(env.path('dir'), 0o500)

        env.fs.shutil_rmtree(env.path('dir'))

        assert env.fs.path_lexists(env.path('dir')) is False

    @real_and_fake()
    def test_the_permissions_of_the_files_inside_do_not_matter(self, env):
        env.fs.mkdir(env.path('dir'))
        env.fs.write_file(env.path('dir/file'), 'a')
        env.fs.chmod(env.path('dir/file'), 0o000)

        env.fs.shutil_rmtree(env.path('dir'))

        assert env.fs.path_lexists(env.path('dir')) is False
