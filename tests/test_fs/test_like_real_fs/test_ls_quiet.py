from trashcli.fslib.real.entries_if_dir_exists import EntriesIfDirExists

from tests.support.put.real_and_fake_env import env, real_and_fake, Env

env = env  # the fixture, imported from its module


class TestLsQuiet:
    @real_and_fake()
    def test_entries_of_an_existing_dir(self, env):
        env.fs.mkdirs(env.path('dir'))
        env.fs.write_file(env.path('dir/a'), 'a')
        env.fs.write_file(env.path('dir/b'), 'b')

        lister = EntriesIfDirExists(env.fs)

        assert sorted(lister.entries_if_dir_exists(
            env.path('dir'))) == ['a', 'b']

    @real_and_fake()
    def test_entries_of_a_missing_dir_are_empty(self, env):
        lister = EntriesIfDirExists(env.fs)

        assert list(lister.entries_if_dir_exists(
            env.path('missing'))) == []
