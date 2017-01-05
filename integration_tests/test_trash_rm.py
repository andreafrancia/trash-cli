from unit_tests.myStringIO import StringIO
from mock import Mock, ANY
from nose.tools import assert_false, assert_raises, assert_equals

from .files import require_empty_dir, write_file
from trashcli.rm import RmCmd, ListTrashinfos
from .trashinfo import a_trashinfo_with_path, a_trashinfo_without_path
from trashcli.trash import ParseError

class TestTrashRm:
    def test_issue69(self):
        self.add_invalid_trashinfo_without_path(1)

        self.trash_rm.run(['trash-rm', 'any-pattern (ignored)'])

        assert_equals('trash-rm: '
                      'sandbox/xdh/Trash/info/1.trashinfo: '
                      'unable to parse \'Path\''
                      '\n'
                      , self.stderr.getvalue())


    def test_integration(self):
        self.add_trashinfo_for(1, 'to/be/deleted')
        self.add_trashinfo_for(2, 'to/be/kept')

        self.trash_rm.run(['trash-rm', 'delete*'])

        self.assert_trashinfo_has_been_deleted(1)
    def setUp(self):
        require_empty_dir('sandbox/xdh')
        self.stderr = StringIO()
        self.trash_rm = RmCmd(environ = {'XDG_DATA_HOME':'sandbox/xdh'}
                         , getuid = 123
                         , list_volumes = lambda:[]
                         , stderr = self.stderr
                         , file_reader = FileSystemReader())

    def add_trashinfo_for(self, index, path):
        write_file(self.trashinfo_from_index(index),
                   a_trashinfo_with_path(path))
    def add_invalid_trashinfo_without_path(self, index):
        write_file(self.trashinfo_from_index(index),
                   a_trashinfo_without_path())
    def trashinfo_from_index(self, index):
        return 'sandbox/xdh/Trash/info/%s.trashinfo' % index

    def assert_trashinfo_has_been_deleted(self, index):
        import os
        filename = self.trashinfo_from_index(index)
        assert_false(os.path.exists(filename),
                'File "%s" still exists' % filename)

from trashcli.fs import FileSystemReader
class TestListing:
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
        write_file(trashinfo_path, a_trashinfo_with_path(path))
    def _trashinfo_path(self, trashdir):
        path = '%s/info/%s.trashinfo' % (trashdir, self.index)
        self.index +=1
        return path



