import pytest

from trashcli.fslib.remove_file_if_exists import RemoveFileIfExists

from tests.support.put.real_and_fake_env import env, real_and_fake, Env

env = env  # the fixture, imported from its module


class TestRemoveFileIfExistsWorkInFakeFsLikeRealFs:
    @pytest.fixture(autouse=True)
    def setup_remover(self, env):  # type: (Env) -> None
        self.remover = RemoveFileIfExists(env.fs, {}, lambda: 123)

    @real_and_fake()
    def test_remove_file_if_exists_removes_a_file(
            self, env):  # type: (Env) -> None
        env.fs.write_file(env.path('file'), 'contents')

        self.remover.remove_file_if_exists(env.path('file'))

        assert env.fs.path_lexists(env.path('file')) is False

    @real_and_fake()
    def test_remove_file_if_exists_ignores_a_missing_file(
            self, env):  # type: (Env) -> None
        self.remover.remove_file_if_exists(env.path('missing'))

        assert env.fs.path_lexists(env.path('missing')) is False

    @real_and_fake()
    def test_remove_file_if_exists_removes_a_dangling_symlink(
            self, env):  # type: (Env) -> None
        env.fs.symlink('missing-target', env.path('link'))

        self.remover.remove_file_if_exists(env.path('link'))

        assert env.fs.path_lexists(env.path('link')) is False

    @real_and_fake()
    def test_remove_file_if_exists_removes_a_dir_with_its_content(
            self, env):  # type: (Env) -> None
        env.fs.mkdirs(env.path('dir'))
        env.fs.write_file(env.path('dir/a'), 'a')

        self.remover.remove_file_if_exists(env.path('dir'))

        assert env.fs.path_lexists(env.path('dir')) is False
