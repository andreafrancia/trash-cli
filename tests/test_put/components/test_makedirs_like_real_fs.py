import errno

import pytest

from tests.support.put.real_and_fake_env import env, real_and_fake

env = env  # the fixture, imported from its module


def errno_of(action):
    with pytest.raises(OSError) as excinfo:
        action()
    return excinfo.value.errno


# Characterization of RealFs.makedirs (it delegates to os.makedirs): FakeFs
# has to behave the same way.
class TestMakedirsLikeRealFs:
    @real_and_fake()
    def test_creates_the_dir_and_its_parents(self, env):
        env.fs.makedirs(env.path('a/b/c'), 0o700)

        assert env.fs.path_isdir(env.path('a')) is True
        assert env.fs.path_isdir(env.path('a/b')) is True
        assert env.fs.path_isdir(env.path('a/b/c')) is True

    @real_and_fake()
    def test_the_last_dir_has_the_given_mode(self, env):
        env.fs.makedirs(env.path('a/b'), 0o700)

        assert env.fs.get_mod(env.path('a/b')) == 0o700

    @real_and_fake()
    def test_an_existing_dir_raises_eexist(self, env):
        env.fs.makedirs(env.path('dir'), 0o700)

        assert errno_of(lambda: env.fs.makedirs(env.path('dir'), 0o700)
                        ) == errno.EEXIST

    @real_and_fake()
    def test_an_existing_file_raises_eexist(self, env):
        env.fs.write_file(env.path('file'), 'a')

        assert errno_of(lambda: env.fs.makedirs(env.path('file'), 0o700)
                        ) == errno.EEXIST

    @real_and_fake()
    def test_under_a_file_raises_enotdir(self, env):
        env.fs.write_file(env.path('file'), 'a')

        assert errno_of(lambda: env.fs.makedirs(env.path('file/dir'), 0o700)
                        ) == errno.ENOTDIR
