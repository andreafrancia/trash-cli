import errno

import pytest

from tests.support.put.real_and_fake_env import env, real_and_fake

env = env  # the fixture, imported from its module


# Characterization of RealFs.remove (os.remove): FakeFs has to behave the same
# way.
class TestRemoveLikeRealFs:
    @real_and_fake()
    def test_removes_a_file(self, env):
        env.fs.write_file(env.path('file'), 'a')

        env.fs.remove(env.path('file'))

        assert env.fs.path_lexists(env.path('file')) is False

    @real_and_fake()
    def test_removes_a_symlink_not_its_target(self, env):
        env.fs.write_file(env.path('target'), 'a')
        env.fs.symlink(env.path('target'), env.path('link'))

        env.fs.remove(env.path('link'))

        assert env.fs.path_lexists(env.path('link')) is False
        assert env.fs.path_lexists(env.path('target')) is True

    @real_and_fake()
    def test_removes_a_dangling_symlink(self, env):
        env.fs.symlink('missing-target', env.path('link'))

        env.fs.remove(env.path('link'))

        assert env.fs.path_lexists(env.path('link')) is False

    @real_and_fake()
    def test_fails_on_a_missing_path(self, env):
        with pytest.raises(OSError) as excinfo:
            env.fs.remove(env.path('missing'))

        assert excinfo.value.errno == errno.ENOENT

    @real_and_fake()
    def test_fails_on_a_dir_and_leaves_it(self, env):
        env.fs.mkdir(env.path('dir'))

        with pytest.raises(OSError):
            env.fs.remove(env.path('dir'))

        assert env.fs.path_isdir(env.path('dir')) is True

    @real_and_fake()
    def test_does_not_touch_the_other_entries(self, env):
        env.fs.write_file(env.path('a'), 'a')
        env.fs.write_file(env.path('b'), 'b')

        env.fs.remove(env.path('a'))

        assert sorted(env.fs.listdir(env.base)) == ['b']
