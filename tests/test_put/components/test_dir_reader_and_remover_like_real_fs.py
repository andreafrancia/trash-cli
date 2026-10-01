from tests.support.put.real_and_fake_env import env, real_and_fake

env = env  # the fixture, imported from its module


# entries_if_dir_exists and remove_file_if_exists live in separate classes on
# the real file system and in FakeFs on the fake one: same answers expected.
class TestDirReaderAndRemoverLikeRealFs:
    @real_and_fake()
    def test_entries_of_an_existing_dir(self, env):
        env.fs.mkdirs(env.path('dir'))
        env.fs.write_file(env.path('dir/a'), 'a')
        env.fs.write_file(env.path('dir/b'), 'b')

        assert sorted(env.dir_reader.entries_if_dir_exists(
            env.path('dir'))) == ['a', 'b']

    @real_and_fake()
    def test_entries_of_a_missing_dir_are_empty(self, env):
        assert list(env.dir_reader.entries_if_dir_exists(
            env.path('missing'))) == []

    @real_and_fake()
    def test_remove_file_if_exists_removes_a_file(self, env):
        env.fs.write_file(env.path('file'), 'contents')

        env.remover.remove_file_if_exists(env.path('file'))

        assert env.fs.path_lexists(env.path('file')) is False

    @real_and_fake()
    def test_remove_file_if_exists_ignores_a_missing_file(self, env):
        env.remover.remove_file_if_exists(env.path('missing'))

        assert env.fs.path_lexists(env.path('missing')) is False

    @real_and_fake()
    def test_remove_file_if_exists_removes_a_dangling_symlink(self, env):
        env.fs.symlink('missing-target', env.path('link'))

        env.remover.remove_file_if_exists(env.path('link'))

        assert env.fs.path_lexists(env.path('link')) is False

    @real_and_fake()
    def test_remove_file_if_exists_removes_a_dir_with_its_content(self, env):
        env.fs.mkdirs(env.path('dir'))
        env.fs.write_file(env.path('dir/a'), 'a')

        env.remover.remove_file_if_exists(env.path('dir'))

        assert env.fs.path_lexists(env.path('dir')) is False
