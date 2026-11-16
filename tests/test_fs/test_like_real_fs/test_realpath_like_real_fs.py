from tests.support.put.real_and_fake_env import env, real_and_fake

env = env  # the fixture, imported from its module


# Characterization of RealFs.realpath (it delegates to os.path.realpath):
# FakeFs has to behave the same way. The base dir itself may be reached
# through a symlink (e.g. /var on macOS): expected paths are built on its
# realpath.
class TestRealpathLikeRealFs:
    @real_and_fake()
    def test_a_file_is_its_own_realpath(self, env):
        env.fs.write_file(env.path('file'), 'a')

        assert (env.fs.realpath(env.path('file')) ==
                env.fs.realpath(env.base) + '/file')

    @real_and_fake()
    def test_a_missing_path_is_returned_as_it_is(self, env):
        assert (env.fs.realpath(env.path('missing/path')) ==
                env.fs.realpath(env.base) + '/missing/path')

    @real_and_fake()
    def test_resolves_a_symlink_to_a_file(self, env):
        env.fs.write_file(env.path('file'), 'a')
        env.fs.symlink('file', env.path('link'))

        assert (env.fs.realpath(env.path('link')) ==
                env.fs.realpath(env.base) + '/file')

    @real_and_fake()
    def test_resolves_a_dangling_symlink_to_its_target(self, env):
        env.fs.symlink('missing-target', env.path('link'))

        assert (env.fs.realpath(env.path('link')) ==
                env.fs.realpath(env.base) + '/missing-target')

    @real_and_fake()
    def test_resolves_a_symlink_in_the_middle_of_the_path(self, env):
        env.fs.mkdirs(env.path('dir'))
        env.fs.write_file(env.path('dir/file'), 'a')
        env.fs.symlink('dir', env.path('link'))

        assert (env.fs.realpath(env.path('link/file')) ==
                env.fs.realpath(env.base) + '/dir/file')

    @real_and_fake()
    def test_resolves_dot_dot(self, env):
        env.fs.mkdirs(env.path('dir'))

        assert (env.fs.realpath(env.path('dir/../file')) ==
                env.fs.realpath(env.base) + '/file')
