from tests.support.put.real_and_fake_env import env, real_and_fake
from trashcli.fslib.force_remover import ForceRemover

env = env  # the fixture, imported from its module


def is_in_home_trash(env, environ, path):
    return ForceRemover(env.fs, environ, lambda: 1000).is_in_home_trash(path)


# ForceRemover adds permissions only where is_in_home_trash() is True.
# The path is compared as it is, while the home trash and the home dir
# are compared after fs.realpath(): what counts is where the trash
# really is, not how its path is written.
class TestIsInHomeTrash:
    @real_and_fake()
    def test_path__is_in_home_trash__when_in_the_default_home_trash(self, env):
        environ = {'HOME': env.path('home')}

        assert is_in_home_trash(
            env, environ, env.path('home/.local/share/Trash/files/dir'))

    @real_and_fake()
    def test_path__is_in_home_trash__when_in_a_trash_under_xdg_data_home_inside_home(self, env):
        environ = {'HOME': env.path('home'),
                   'XDG_DATA_HOME': env.path('home/data')}

        assert is_in_home_trash(env, environ, env.path('home/data/Trash/files/dir'))

    @real_and_fake()
    def test_path__is_not_in_home_trash__when_home_is_unset(self, env):
        environ = {'XDG_DATA_HOME': env.path('home/data')}

        assert not is_in_home_trash(
            env, environ, env.path('home/data/Trash/files/dir'))

    @real_and_fake()
    def test_path__is_not_in_home_trash__when_outside_the_home_trash(self, env):
        environ = {'HOME': env.path('home')}

        assert not is_in_home_trash(env, environ, env.path('home/dir'))

    @real_and_fake()
    def test_the_home_trash_itself__is_not_in_home_trash(self, env):
        environ = {'HOME': env.path('home')}

        assert not is_in_home_trash(
            env, environ, env.path('home/.local/share/Trash'))

    @real_and_fake()
    def test_path__is_not_in_home_trash__when_in_a_sibling_named_like_the_trash(self, env):
        environ = {'HOME': env.path('home')}

        assert not is_in_home_trash(
            env, environ, env.path('home/.local/share/Trash2/files/dir'))

    @real_and_fake()
    def test_path__is_not_in_home_trash__when_xdg_data_home_is_outside_home(self, env):
        environ = {'HOME': env.path('home'),
                   'XDG_DATA_HOME': env.path('data')}

        assert not is_in_home_trash(env, environ, env.path('data/Trash/files/dir'))

    @real_and_fake()
    def test_path__is_not_in_home_trash__when_in_a_volume_trash(self, env):
        environ = {'HOME': env.path('home')}

        assert not is_in_home_trash(
            env, environ, env.path('volume/.Trash-1000/files/dir'))

