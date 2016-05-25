from trashcli.trash import TrashDirectory

from .files import require_empty_dir
from .files import write_file
from nose.tools import assert_equal

# Try Python 2 import; if ImportError occurs, use Python 3 import
try:
    from nose.tools import assert_items_equal
except ImportError:
    from nose.tools import assert_count_equal as assert_items_equal

# Try Python 3 import; if ImportError occurs, use Python 2 import
try:
    from unittest.mock import Mock
except ImportError:
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

        assert_equal(['sandbox/info/foo.trashinfo'], result)

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

        assert_equal([], result)

    def test_non_trashinfo_should_reported_as_a_warn(self):
        write_file('sandbox/info/not-a-trashinfo')

        self.list_trashinfos()

        self.logger.warning.assert_called_with('Non .trashinfo file in info dir')

    def list_trashinfos(self):
        return list(self.trash_dir.all_info_files())


