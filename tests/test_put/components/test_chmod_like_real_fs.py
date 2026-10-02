import errno

import pytest

from tests.support.put.real_and_fake_env import env, real_and_fake

env = env  # the fixture, imported from its module


# Characterization of RealFs.chmod and RealFs.get_mod (they delegate to
# os.chmod and os.lstat): FakeFs has to behave the same way.
class TestChmodLikeRealFs:
    @real_and_fake()
    def test_chmod_on_a_file(self, env):
        env.fs.write_file(env.path('file'), 'a')

        env.fs.chmod(env.path('file'), 0o123)

        assert env.fs.get_mod(env.path('file')) == 0o123

    @real_and_fake()
    def test_chmod_on_a_dir(self, env):
        env.fs.mkdir(env.path('dir'))

        env.fs.chmod(env.path('dir'), 0o300)

        assert env.fs.get_mod(env.path('dir')) == 0o300
        env.fs.chmod(env.path('dir'), 0o700)

    @real_and_fake()
    def test_chmod_can_set_the_sticky_bit(self, env):
        env.fs.mkdir(env.path('dir'))

        env.fs.chmod(env.path('dir'), 0o1755)

        assert env.fs.get_mod(env.path('dir')) == 0o1755
        assert env.fs.has_sticky_bit(env.path('dir')) is True

    @real_and_fake()
    def test_chmod_can_unset_the_sticky_bit(self, env):
        env.fs.mkdir(env.path('dir'))
        env.fs.chmod(env.path('dir'), 0o1755)

        env.fs.chmod(env.path('dir'), 0o755)

        assert env.fs.get_mod(env.path('dir')) == 0o755
        assert env.fs.has_sticky_bit(env.path('dir')) is False

    @real_and_fake()
    def test_chmod_follows_a_symlink(self, env):
        env.fs.write_file(env.path('file'), 'a')
        env.fs.symlink('file', env.path('link'))

        env.fs.chmod(env.path('link'), 0o123)

        assert env.fs.get_mod(env.path('file')) == 0o123

    @real_and_fake()
    def test_chmod_on_a_missing_path_raises_enoent(self, env):
        with pytest.raises(OSError) as excinfo:
            env.fs.chmod(env.path('missing'), 0o755)

        assert excinfo.value.errno == errno.ENOENT

    @real_and_fake()
    def test_get_mod_on_a_missing_path_raises_enoent(self, env):
        with pytest.raises(OSError) as excinfo:
            env.fs.get_mod(env.path('missing'))

        assert excinfo.value.errno == errno.ENOENT
