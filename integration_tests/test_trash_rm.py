from trashcli.rm import Main
from files import require_empty_dir, write_file
from trashinfo import a_trashinfo_with_path
from mock import Mock
from StringIO import StringIO
from nose.tools import assert_true, assert_false, assert_raises

class TestTrashRm:
    def test_integration(self):
        trash_rm = Main()
        trash_rm.environ = {}
        trash_rm.list_volumes = lambda:[]
        trash_rm.getuid = 123
        trash_rm.stderr = StringIO()

        self.add_trashinfo_for(1, 'to/be/deleted')
        self.add_trashinfo_for(2, 'to/be/kept')

        trash_rm.run(['delete*'])

        assert_raises(AssertionError,
                      lambda:self.assert_trashinfo_has_been_deleted(1))
    def setUp(self):
        require_empty_dir('sandbox/xdh')

    def add_trashinfo_for(self, index, path):
        write_file(self.trashinfo_from_index(index),
                   a_trashinfo_with_path(path))
    def trashinfo_from_index(self, index):
        return 'sandbox/xdh/Trash/info/%s.trashinfo' % index

    def assert_trashinfo_has_been_deleted(self, index):
        import os
        filename = self.trashinfo_from_index(index)
        assert_false(os.path.exists(filename),
                'File "%s" still exists' % filename)

