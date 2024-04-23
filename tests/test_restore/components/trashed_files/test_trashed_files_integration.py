import datetime
import unittest

from mock import Mock

from tests.support.files import make_file, require_empty_dir
from tests.support.dirs.remove_dir_if_exists import remove_dir_if_exists
from trashcli.fs import remove_file
from trashcli.restore.file_system import RealFileReader
from trashcli.restore.info_dir_searcher import InfoDirSearcher, FileFound
from trashcli.restore.trashed_files import TrashedFiles


class TestTrashedFilesIntegration(unittest.TestCase):
    def setUp(self):
        self.logger = Mock(spec=[])
        self.searcher = Mock(spec=InfoDirSearcher)
        self.trashed_files = TrashedFiles(self.logger,
                                          RealFileReader(),
                                          self.searcher)

    def test(self):
        require_empty_dir('info')
        self.searcher.all_file_in_info_dir.return_value = [
            FileFound('trashinfo', 'info/info_path.trashinfo', '/volume')
        ]
        make_file('info/info_path.trashinfo',
                  'Path=name\nDeletionDate=2001-01-01T10:10:10')

        trashed_files = list(self.trashed_files.all_trashed_files(None))

        trashed_file = trashed_files[0]
        assert '/volume/name' == trashed_file.original_location
        assert (datetime.datetime(2001, 1, 1, 10, 10, 10) ==
                trashed_file.deletion_date)
        assert 'info/info_path.trashinfo' == trashed_file.info_file
        assert 'files/info_path' == trashed_file.original_file

    def tearDown(self):
        remove_file('info/info_path.trashinfo')
        remove_dir_if_exists('info')
