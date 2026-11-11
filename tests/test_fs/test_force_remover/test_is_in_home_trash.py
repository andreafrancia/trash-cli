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
    def test_true_for_a_path_in_the_default_home_trash(self, env):
        environ = {'HOME': env.path('home')}

        assert is_in_home_trash(
            env, environ, env.path('home/.local/share/Trash/files/dir'))

    @real_and_fake()
    def test_true_for_a_path_in_a_trash_under_xdg_data_home_inside_home(self, env):
        environ = {'HOME': env.path('home'),
                   'XDG_DATA_HOME': env.path('home/data')}

        assert is_in_home_trash(env, environ, env.path('home/data/Trash/files/dir'))

    @real_and_fake()
    def test_false_without_home(self, env):
        environ = {'XDG_DATA_HOME': env.path('home/data')}

        assert not is_in_home_trash(
            env, environ, env.path('home/data/Trash/files/dir'))

    @real_and_fake()
    def test_false_for_a_path_outside_the_home_trash(self, env):
        environ = {'HOME': env.path('home')}

        assert not is_in_home_trash(env, environ, env.path('home/dir'))

    @real_and_fake()
    def test_false_for_the_home_trash_itself(self, env):
        environ = {'HOME': env.path('home')}

        assert not is_in_home_trash(
            env, environ, env.path('home/.local/share/Trash'))

    @real_and_fake()
    def test_false_for_a_sibling_whose_name_starts_like_the_trash(self, env):
        environ = {'HOME': env.path('home')}

        assert not is_in_home_trash(
            env, environ, env.path('home/.local/share/Trash2/files/dir'))

    @real_and_fake()
    def test_false_when_xdg_data_home_is_outside_home(self, env):
        environ = {'HOME': env.path('home'),
                   'XDG_DATA_HOME': env.path('data')}

        assert not is_in_home_trash(env, environ, env.path('data/Trash/files/dir'))

    @real_and_fake()
    def test_false_for_a_path_in_a_volume_trash(self, env):
        environ = {'HOME': env.path('home')}

        assert not is_in_home_trash(
            env, environ, env.path('volume/.Trash-1000/files/dir'))


# The cases where fs.realpath() changes the answer: a symlink or a '..'
# makes the written path and the real location disagree.
class TestIsInHomeTrashNeedsRealpath:
    @real_and_fake()
    def test_false_when_xdg_data_home_is_written_inside_home_but_links_outside(self, env):
        # ~/data -> /shared: the trash is written as ~/data/Trash, but it
        # really is /shared/Trash, outside the home dir
        env.fs.mkdirs(env.path('home'))
        env.fs.mkdirs(env.path('shared'))
        env.fs.symlink(env.path('shared'), env.path('home/data'))
        environ = {'HOME': env.path('home'),
                   'XDG_DATA_HOME': env.path('home/data')}

        assert not is_in_home_trash(env, environ, env.path('home/data/Trash/files/dir'))

    @real_and_fake()
    def test_false_when_xdg_data_home_is_written_inside_home_but_dots_go_outside(self, env):
        environ = {'HOME': env.path('home'),
                   'XDG_DATA_HOME': env.path('home/../shared')}

        assert not is_in_home_trash(
            env, environ, env.path('home/../shared/Trash/files/dir'))

    @real_and_fake()
    def test_true_when_xdg_data_home_is_written_outside_home_but_links_inside(self, env):
        # /data -> ~/data: the trash is written as /data/Trash, but it
        # really is ~/data/Trash, inside the home dir
        env.fs.mkdirs(env.path('home/data'))
        env.fs.symlink(env.path('home/data'), env.path('data'))
        environ = {'HOME': env.path('home'),
                   'XDG_DATA_HOME': env.path('data')}

        assert is_in_home_trash(env, environ, env.path('data/Trash/files/dir'))

    @real_and_fake()
    def test_true_when_home_is_a_symlink(self, env):
        # /home/user -> /disk/user, as when the home dir is on another disk:
        # the realpath of the trash must be compared with the realpath of
        # the home dir, not with the home dir as it is written
        env.fs.mkdirs(env.path('disk/user'))
        env.fs.symlink(env.path('disk/user'), env.path('home'))
        environ = {'HOME': env.path('home')}

        assert is_in_home_trash(
            env, environ, env.path('home/.local/share/Trash/files/dir'))
