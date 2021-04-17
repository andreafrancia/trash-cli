import unittest

from unit_tests.myStringIO import StringIO
from mock import Mock, ANY

from .files import require_empty_dir, make_file
from unit_tests.support import MyPath
from trashcli.rm import RmCmd, ListTrashinfos
from .fake_trash_dir import a_trashinfo_with_path, a_trashinfo_without_path
from trashcli.fs import FileSystemReader


class TestTrashRm(unittest.TestCase):
    def setUp(self):
        self.xdg_data_home = MyPath.make_temp_dir()
        self.stderr = StringIO()
        self.trash_rm = RmCmd(environ = {'XDG_DATA_HOME': self.xdg_data_home}
                         , getuid = 123
                         , list_volumes = lambda:[]
                         , stderr = self.stderr
                         , file_reader = FileSystemReader())

    def test_issue69(self):
        self.add_trashinfo("foo.trashinfo", a_trashinfo_without_path())

        self.trash_rm.run(['trash-rm', 'ignored'])

        assert (self.stderr.getvalue() ==
                "trash-rm: %s/Trash/info/foo.trashinfo: unable to parse 'Path'"
                '\n' % self.xdg_data_home)


    def test_integration(self):
        self.add_trashinfo("1.trashinfo", a_trashinfo_with_path('to/be/deleted'))
        self.add_trashinfo("2.trashinfo", a_trashinfo_with_path('to/be/kept'))

        self.trash_rm.run(['trash-rm', 'delete*'])

        self.assert_trashinfo_has_been_deleted("1.trashinfo")

    def add_trashinfo(self, trashinfo_name, contents):
        make_file(self.trashinfo_path(trashinfo_name), contents)

    def trashinfo_path(self, trashinfo_name):
        return self.xdg_data_home / 'Trash/info' / trashinfo_name

    def assert_trashinfo_has_been_deleted(self, trashinfo_name):
        import os
        path = self.trashinfo_path(trashinfo_name)
        assert not os.path.exists(path), 'File "%s" still exists' % path

    def tearDown(self):
        self.xdg_data_home.clean_up()


class TestListing(unittest.TestCase):
    def setUp(self):
        require_empty_dir('sandbox')
        self.out = Mock()
        self.listing = ListTrashinfos(self.out,
                                      FileSystemReader(),
                                      None)
        self.index = 0

    def test_should_report_original_location(self):
        self.add_trashinfo('/foo')

        self.listing.list_from_volume_trashdir('sandbox/Trash', '/')

        self.out.assert_called_with('/foo', ANY)

    def test_should_report_trashinfo_path(self):
        self.add_trashinfo(trashinfo_path='sandbox/Trash/info/a.trashinfo')

        self.listing.list_from_volume_trashdir('sandbox/Trash', '/')

        self.out.assert_called_with(ANY, 'sandbox/Trash/info/a.trashinfo')

    def test_should_handle_volume_trashdir(self):
        self.add_trashinfo(trashinfo_path='sandbox/.Trash/123/info/a.trashinfo')

        self.listing.list_from_volume_trashdir('sandbox/.Trash/123',
                                               '/fake/vol')

        self.out.assert_called_with(ANY, 'sandbox/.Trash/123/info/a.trashinfo')

    def test_should_absolutize_relative_path_for_volume_trashdir(self):
        self.add_trashinfo(path='foo/bar', trashdir='sandbox/.Trash/501')

        self.listing.list_from_volume_trashdir('sandbox/.Trash/501',
                                               '/fake/vol')

        self.out.assert_called_with('/fake/vol/foo/bar', ANY)

    def add_trashinfo(self, path='unspecified/original/location',
                            trashinfo_path=None,
                            trashdir='sandbox/Trash'):
        trashinfo_path = trashinfo_path or self._trashinfo_path(trashdir)
        make_file(trashinfo_path, a_trashinfo_with_path(path))
    def _trashinfo_path(self, trashdir):
        path = '%s/info/%s.trashinfo' % (trashdir, self.index)
        self.index +=1
        return path
