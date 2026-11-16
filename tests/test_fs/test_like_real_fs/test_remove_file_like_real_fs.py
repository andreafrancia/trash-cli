from tests.support.put.real_and_fake_env import env, real_and_fake

env = env  # the fixture, imported from its module


# Characterization of RealFs.remove_file: FakeFs has to behave the same way.
class TestRemoveFileLikeRealFs:
    @real_and_fake()
    def test_removes_a_file(self, env):
        env.fs.write_file(env.path('file'), 'a')

        env.fs.remove_file(env.path('file'))

        assert env.fs.path_lexists(env.path('file')) is False

    @real_and_fake()
    def test_removes_an_empty_dir(self, env):
        env.fs.mkdir(env.path('dir'))

        env.fs.remove_file(env.path('dir'))

        assert env.fs.path_lexists(env.path('dir')) is False

    @real_and_fake()
    def test_removes_a_dir_with_its_content(self, env):
        env.fs.mkdirs(env.path('dir/subdir'))
        env.fs.write_file(env.path('dir/a'), 'a')
        env.fs.write_file(env.path('dir/subdir/b'), 'b')

        env.fs.remove_file(env.path('dir'))

        assert env.fs.path_lexists(env.path('dir')) is False

    @real_and_fake()
    def test_removes_a_dangling_symlink(self, env):
        env.fs.symlink('missing-target', env.path('link'))

        env.fs.remove_file(env.path('link'))

        assert env.fs.path_lexists(env.path('link')) is False

    @real_and_fake()
    def test_ignores_a_missing_path(self, env):
        env.fs.remove_file(env.path('missing'))

        assert env.fs.path_lexists(env.path('missing')) is False

    @real_and_fake()
    def test_does_not_touch_the_other_entries(self, env):
        env.fs.write_file(env.path('a'), 'a')
        env.fs.write_file(env.path('b'), 'b')

        env.fs.remove_file(env.path('a'))

        assert sorted(env.fs.listdir(env.base)) == ['b']
