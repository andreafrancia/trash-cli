from trashcli.trash2 import AvailableInfoDirs
from nose.tools import istest, assert_items_equal

@istest
class Describe_AvailableInfoDirs:
    def test_it_returns_nothing_on_no_environment_variable(self):
        self.with_environ({})
        self.should_return()   # nothing

    def test_it_honours_the_xdg_datahome(self):
        self.with_environ({'XDG_DATA_HOME':'/alternate/xdg/data/home'})
        self.should_return('/alternate/xdg/data/home/Trash/info')

    def test_it_uses_the_default_value_of_xdg_datahome(self):
        self.with_environ( {'HOME':'/home/foo'})
        self.should_return('/home/foo/.local/share/Trash/info')

    def test_it_considers_trashcans_volumes(self):
        self.with_volumes('/mnt')
        self.with_user_id('123')

        self.should_return('/mnt/.Trash/123/info',
                           '/mnt/.Trash-123/info')

    def test_it_works_with_root_volume(self):
        self.with_volumes('/')
        self.with_user_id('123')

        self.should_return('/.Trash/123/info',
                           '/.Trash-123/info')

    def with_environ(self, environ):
        self.environ = environ
    def with_volumes(self, *volumes_paths):
        self.list_volumes = lambda:volumes_paths
    def with_user_id(self, uid):
        self.getuid = lambda: uid

    def should_return(self, *expected_result):
        finder = AvailableInfoDirs(
                environ      = self.environ,
                getuid       = self.getuid,
                list_volumes = self.list_volumes)

        result = []

        finder.for_each_infodir_and_volume(
                lambda path, volume: result.append(path))

        assert_items_equal(expected_result, result)

    def setUp(self):
        self.environ      = {}
        self.getuid       = lambda:None
        self.list_volumes = lambda:[]

