import unittest

from trashcli.restore import TrashDirectory

from integration_tests.files import require_empty_dir
from integration_tests.files import make_file
from unit_tests.tools import assert_items_equal
from nose.tools import assert_equal
from mock import Mock


class TestTrashDirectory(unittest.TestCase):
    def setUp(self):
        require_empty_dir('sandbox')
        self.trash_dir = TrashDirectory()
        self.logger = Mock()
        self.trash_dir.logger = self.logger


    def test_should_list_a_trashinfo(self):
        make_file('sandbox/info/foo.trashinfo')

        result = self.list_trashinfos()

        assert_equal([('trashinfo', 'sandbox/info/foo.trashinfo')], result)

    def test_should_list_multiple_trashinfo(self):
        make_file('sandbox/info/foo.trashinfo')
        make_file('sandbox/info/bar.trashinfo')
        make_file('sandbox/info/baz.trashinfo')

        result = self.list_trashinfos()

        assert_items_equal([('trashinfo', 'sandbox/info/foo.trashinfo'),
                            ('trashinfo', 'sandbox/info/baz.trashinfo'),
                            ('trashinfo', 'sandbox/info/bar.trashinfo')],
                           result)

    def test_non_trashinfo_should_reported_as_a_warn(self):
        make_file('sandbox/info/not-a-trashinfo')

        result = self.list_trashinfos()

        assert_items_equal([('non_trashinfo', 'sandbox/info/not-a-trashinfo')],
                           result)

    def list_trashinfos(self):
        return list(self.trash_dir.all_info_files('sandbox'))


