import datetime
import unittest

from mock import Mock, call
from trashcli.restore import TrashedFiles

from ..files import make_file, require_empty_dir


class TestTrashedFiles(unittest.TestCase):
    def setUp(self):
        self.trash_directories = Mock(spec=['trash_directories_or_user'])
        self.trash_directory = Mock(spec=['all_info_files'])
        self.contents_of = Mock()
        self.logger = Mock(spec=[])
        self.trashed_files = TrashedFiles(self.logger,
                                          self.trash_directories,
                                          self.trash_directory,
                                          self.contents_of)

    def test_something(self):
        self.trash_directories.trash_directories_or_user.return_value = \
            [("path", "/volume")]
        self.contents_of.return_value = 'Path=name\nDeletionDate=2001-01-01T10:10:10'
        self.trash_directory.all_info_files.return_value = \
            [('trashinfo', 'info/info_path.trashinfo')]

        trashed_files = list(self.trashed_files.all_trashed_files([], None))

        trashed_file = trashed_files[0]
        assert '/volume/name' == trashed_file.original_location
        assert (datetime.datetime(2001, 1, 1, 10, 10, 10) ==
                trashed_file.deletion_date)
        assert 'info/info_path.trashinfo' == trashed_file.info_file
        assert 'files/info_path' == trashed_file.original_file
        assert ([call.trash_directories_or_user([], None)] ==
                self.trash_directories.mock_calls)
