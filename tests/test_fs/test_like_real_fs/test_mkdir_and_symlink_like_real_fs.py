import errno

import pytest

from tests.support.put.real_and_fake_env import env, real_and_fake

env = env  # the fixture, imported from its module


def errno_of(action):
    with pytest.raises(OSError) as excinfo:
        action()
    return excinfo.value.errno


# Characterization of RealFs.mkdir and RealFs.symlink (they delegate to
# os.mkdir and os.symlink): FakeFs has to behave the same way.
class TestMkdirAndSymlinkLikeRealFs:
    @real_and_fake()
    def test_mkdir_creates_an_empty_dir(self, env):
        env.fs.mkdir(env.path('dir'))

        assert env.fs.path_isdir(env.path('dir')) is True
        assert sorted(env.fs.listdir(env.path('dir'))) == []

    @real_and_fake()
    def test_mkdir_does_not_create_the_parents(self, env):
        assert errno_of(lambda: env.fs.mkdir(env.path('missing/dir'))
                        ) == errno.ENOENT
        assert env.fs.path_exists(env.path('missing')) is False

    @real_and_fake()
    def test_mkdir_on_an_existing_dir_raises_eexist(self, env):
        env.fs.mkdir(env.path('dir'))

        assert errno_of(lambda: env.fs.mkdir(env.path('dir'))) == errno.EEXIST

    @real_and_fake()
    def test_mkdir_on_an_existing_file_raises_eexist(self, env):
        env.fs.write_file(env.path('file'), 'a')

        assert errno_of(lambda: env.fs.mkdir(env.path('file'))) == errno.EEXIST

    @real_and_fake()
    def test_symlink_creates_a_link_with_the_target_as_written(self, env):
        env.fs.symlink('relative/target', env.path('link'))

        assert env.fs.readlink(env.path('link')) == 'relative/target'
        assert env.fs.is_symlink(env.path('link')) is True

    @real_and_fake()
    def test_symlink_can_be_dangling(self, env):
        env.fs.symlink('missing-target', env.path('link'))

        assert env.fs.path_lexists(env.path('link')) is True
        assert env.fs.path_exists(env.path('link')) is False

    @real_and_fake()
    def test_symlink_over_an_existing_path_raises_eexist(self, env):
        env.fs.write_file(env.path('file'), 'a')

        assert errno_of(lambda: env.fs.symlink('target', env.path('file'))
                        ) == errno.EEXIST

    @real_and_fake()
    def test_symlink_in_a_missing_dir_raises_enoent(self, env):
        assert errno_of(lambda: env.fs.symlink('target', env.path('missing/link'))
                        ) == errno.ENOENT
