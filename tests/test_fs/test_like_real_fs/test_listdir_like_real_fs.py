import errno

import pytest

from tests.support.put.real_and_fake_env import env, real_and_fake

env = env  # the fixture, imported from its module


def errno_of_listdir(env, path):
    with pytest.raises(OSError) as excinfo:
        env.fs.listdir(path)
    return excinfo.value.errno


# Characterization of RealFs.listdir (it delegates to os.listdir): FakeFs
# has to behave the same way.
class TestListdirLikeRealFs:
    @real_and_fake()
    def test_empty_dir(self, env):
        env.fs.mkdirs(env.path('dir'))

        assert sorted(env.fs.listdir(env.path('dir'))) == []

    @real_and_fake()
    def test_returns_a_list_of_names_not_paths(self, env):
        env.fs.mkdirs(env.path('dir'))
        env.fs.write_file(env.path('dir/a'), 'a')

        result = env.fs.listdir(env.path('dir'))

        assert isinstance(result, list)
        assert sorted(result) == ['a']

    @real_and_fake()
    def test_does_not_include_dot_and_dotdot(self, env):
        env.fs.mkdirs(env.path('dir'))

        assert '.' not in env.fs.listdir(env.path('dir'))
        assert '..' not in env.fs.listdir(env.path('dir'))

    @real_and_fake()
    def test_lists_files_dirs_and_hidden_entries(self, env):
        env.fs.mkdirs(env.path('dir/subdir'))
        env.fs.write_file(env.path('dir/file'), 'a')
        env.fs.write_file(env.path('dir/.hidden'), 'a')

        assert sorted(env.fs.listdir(env.path('dir'))) == [
            '.hidden', 'file', 'subdir']

    @real_and_fake()
    def test_is_not_recursive(self, env):
        env.fs.mkdirs(env.path('dir/subdir'))
        env.fs.write_file(env.path('dir/subdir/nested'), 'a')

        assert sorted(env.fs.listdir(env.path('dir'))) == ['subdir']

    @real_and_fake()
    def test_lists_dangling_symlinks(self, env):
        env.fs.mkdirs(env.path('dir'))
        env.fs.symlink('missing-target', env.path('dir/link'))

        assert sorted(env.fs.listdir(env.path('dir'))) == ['link']

    @real_and_fake()
    def test_follows_a_symlink_to_a_dir(self, env):
        env.fs.mkdirs(env.path('dir'))
        env.fs.write_file(env.path('dir/a'), 'a')
        env.fs.symlink(env.path('dir'), env.path('link'))

        assert sorted(env.fs.listdir(env.path('link'))) == ['a']

    @real_and_fake()
    def test_missing_dir_raises_enoent(self, env):
        assert errno_of_listdir(env, env.path('missing')) == errno.ENOENT

    @real_and_fake()
    def test_missing_parent_raises_enoent(self, env):
        assert errno_of_listdir(env, env.path('missing/dir')) == errno.ENOENT

    @real_and_fake()
    def test_dangling_symlink_raises_enoent(self, env):
        env.fs.symlink('missing-target', env.path('link'))

        assert errno_of_listdir(env, env.path('link')) == errno.ENOENT

    @real_and_fake()
    def test_file_raises_enotdir(self, env):
        env.fs.write_file(env.path('file'), 'a')

        assert errno_of_listdir(env, env.path('file')) == errno.ENOTDIR

    @real_and_fake()
    def test_symlink_to_a_file_raises_enotdir(self, env):
        env.fs.write_file(env.path('file'), 'a')
        env.fs.symlink(env.path('file'), env.path('link'))

        assert errno_of_listdir(env, env.path('link')) == errno.ENOTDIR
