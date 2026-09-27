import datetime

from tests.support.files import require_empty_dir, make_file, remove_file
from tests.support.py2mock import Mock

from tests.support.dirs import remove_dir_if_exists
from trashcli.put.fs.real_volume_path_fs import RealVolumePathFs
from trashcli.restore.real_restore_fs import RealFileReaderFs
from trashcli.restore.info_dir_searcher import InfoDirSearcher, FileFound
from trashcli.restore.trashed_files import TrashedFiles

# Integration test of TrashedFiles with the real file reader (the searcher
# is mocked). The .trashinfo is written for real under ./info (relative to
# the current working directory of the test run).
class TestTrashedFilesIntegration:
    def setup_method(self):
        self.logger = Mock(spec=[])
        self.searcher = Mock(spec=InfoDirSearcher)
        self.trashed_files = TrashedFiles(self.logger,
                                          RealFileReaderFs(),
                                          self.searcher,
                                          RealVolumePathFs())

    # Purpose: in a trash dir on a volume other than '/' ('/volume') a
    # relative Path= is resolved against that volume ('/volume/name'); the
    # deletion date, the info file path and the backup copy path
    # ('files/info_path', derived from the relative info path) are filled in
    # reading the file through the real filesystem.
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

    def teardown_method(self):
        remove_file('info/info_path.trashinfo')
        remove_dir_if_exists('info')
