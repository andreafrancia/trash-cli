from trashcli.trash import TrashDirectory

from .files import require_empty_dir
from .files import write_file
from unit_tests.tools import assert_items_equal
from nose.tools import assert_equals
from mock import Mock

class TestWhenListingTrashinfo:
    def setUp(self):
        require_empty_dir('sandbox')
        self.trash_dir = TrashDirectory('sandbox', '/')
        self.logger = Mock()
        self.trash_dir.logger = self.logger


    def test_should_list_a_trashinfo(self):
        write_file('sandbox/info/foo.trashinfo')

        result = self.list_trashinfos()

        assert_equals(['sandbox/info/foo.trashinfo'], result)

    def test_should_list_multiple_trashinfo(self):
        write_file('sandbox/info/foo.trashinfo')
        write_file('sandbox/info/bar.trashinfo')
        write_file('sandbox/info/baz.trashinfo')

        result = self.list_trashinfos()

        assert_items_equal(['sandbox/info/foo.trashinfo',
                            'sandbox/info/baz.trashinfo',
                            'sandbox/info/bar.trashinfo'], result)

    def test_should_ignore_non_trashinfo(self):
        write_file('sandbox/info/not-a-trashinfo')

        result = self.list_trashinfos()

        assert_equals([], result)

    def test_non_trashinfo_should_reported_as_a_warn(self):
        write_file('sandbox/info/not-a-trashinfo')

        self.list_trashinfos()

        self.logger.warning.assert_called_with('Non .trashinfo file in info dir')

    def list_trashinfos(self):
        return list(self.trash_dir.all_info_files())


