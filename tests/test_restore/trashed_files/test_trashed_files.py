import datetime
import unittest

from mock import Mock

from trashcli.restore.file_system import FakeFileReader
from trashcli.restore.info_dir_searcher import InfoDirSearcher, FileFound
from trashcli.restore.trashed_file import TrashedFiles


class TestTrashedFiles(unittest.TestCase):
    def setUp(self):
        self.contents_of = Mock()
        self.file_reader = FakeFileReader()
        self.logger = Mock(spec=[])
        self.searcher = Mock(spec=InfoDirSearcher)
        self.trashed_files = TrashedFiles(self.logger,
                                          self.file_reader,
                                          self.searcher)

    def test(self):
        self.searcher.all_file_in_info_dir.return_value = [
            FileFound('trashinfo', 'info/info_path.trashinfo', '/volume')
        ]
        self.file_reader.set_content(
            'Path=name\nDeletionDate=2001-01-01T10:10:10')

        trashed_files = list(self.trashed_files.all_trashed_files(None))

        trashed_file = trashed_files[0]
        assert '/volume/name' == trashed_file.original_location
        assert (datetime.datetime(2001, 1, 1, 10, 10, 10) ==
                trashed_file.deletion_date)
        assert 'info/info_path.trashinfo' == trashed_file.info_file
        assert 'files/info_path' == trashed_file.original_file
