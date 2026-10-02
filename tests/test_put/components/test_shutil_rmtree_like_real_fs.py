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
