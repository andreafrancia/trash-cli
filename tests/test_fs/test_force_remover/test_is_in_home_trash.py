from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.fslib.force_remover import ForceRemover


# ForceRemover adds permissions only where is_in_home_trash() is True.
# The path is compared as it is, while the home trash and the home dir
# are compared after fs.realpath(): what counts is where the trash
# really is, not how its path is written.
class TestIsInHomeTrash:
    def setup_method(self):
        self.fs = FakeFs()

    def is_in_home_trash(self, environ, path):
        return ForceRemover(self.fs, environ, lambda: 1000).is_in_home_trash(path)

    def test_path__is_in_home_trash__when_in_the_default_home_trash(self):
        environ = {'HOME': '/home'}

        assert self.is_in_home_trash(
            environ, '/home/.local/share/Trash/files/dir')

    def test_path__is_in_home_trash__when_in_a_trash_under_xdg_data_home_inside_home(self):
        environ = {'HOME': '/home', 'XDG_DATA_HOME': '/home/data'}

        assert self.is_in_home_trash(environ, '/home/data/Trash/files/dir')

    def test_path__is_not_in_home_trash__when_home_is_unset(self):
        environ = {'XDG_DATA_HOME': '/home/data'}

        assert not self.is_in_home_trash(environ, '/home/data/Trash/files/dir')

    def test_path__is_not_in_home_trash__when_outside_the_home_trash(self):
        environ = {'HOME': '/home'}

        assert not self.is_in_home_trash(environ, '/home/dir')

    def test_the_home_trash_itself__is_not_in_home_trash(self):
        environ = {'HOME': '/home'}

        assert not self.is_in_home_trash(environ, '/home/.local/share/Trash')

    def test_path__is_not_in_home_trash__when_in_a_sibling_named_like_the_trash(self):
        environ = {'HOME': '/home'}

        assert not self.is_in_home_trash(
            environ, '/home/.local/share/Trash2/files/dir')

    def test_path__is_not_in_home_trash__when_xdg_data_home_is_outside_home(self):
        environ = {'HOME': '/home', 'XDG_DATA_HOME': '/data'}

        assert not self.is_in_home_trash(environ, '/data/Trash/files/dir')

    def test_path__is_not_in_home_trash__when_in_a_volume_trash(self):
        environ = {'HOME': '/home'}

        assert not self.is_in_home_trash(environ, '/volume/.Trash-1000/files/dir')
