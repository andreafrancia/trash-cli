import datetime
import unittest

from six import StringIO

from tests.support.put.fake_fs.fake_fs import FakeFs
from tests.test_restore.support.fake_logger import FakeLogger
from tests.test_restore.support.restore_fake_fs import RestoreFakeFs
from trashcli.restore.info_dir_searcher import InfoDirSearcher
from trashcli.restore.info_files import InfoFiles
from trashcli.restore.trash_directories import TrashDirectories
from trashcli.restore.trashed_file import TrashedFile
from trashcli.restore.trashed_files import TrashedFiles


class TestTrashedFiles(unittest.TestCase):
    def setUp(self):
        self.fs = FakeFs()
        self.out = StringIO()
        self.logger = FakeLogger(self.out)

        class FakeTrashDirectories(TrashDirectories):
            def list_trash_dirs(self, trash_dir_from_cli):
                return [('/trash-dir', '/')]

        self.searcher = InfoDirSearcher(FakeTrashDirectories(),
                                        InfoFiles(RestoreFakeFs(self.fs)))
        self.trashed_files = TrashedFiles(self.logger,
                                          RestoreFakeFs(self.fs),
                                          self.searcher)
        self.fs.mkdir_p("/trash-dir/info")

    def test(self):
        self.fs.write_file('/trash-dir/info/info_path.trashinfo',
                           'Path=name\n'
                           'DeletionDate=2001-01-01T10:10:10')

        trashed_files = list(self.trashed_files.all_trashed_files(None))

        assert {
                   'trashed_files': trashed_files,
                   'out': self.out.getvalue()} == {
                   'trashed_files': [
                       TrashedFile('/name',
                                   datetime.datetime(2001, 1, 1,
                                                     10, 10,
                                                     10),
                                   '/trash-dir/info/info_path.trashinfo',
                                   '/trash-dir/files/info_path'),
                   ],
                   'out': ''
               }

    def test_on_non_trashinfo(self):
        self.fs.touch('/trash-dir/info/info_path.non-trashinfo')

        trashed_files = list(self.trashed_files.all_trashed_files(None))

        assert {
                   'trashed_files': trashed_files,
                   'out': self.out.getvalue()} == {
                   'trashed_files': [],
                   'out': 'WARN: Non .trashinfo file in info dir\n'
               }

    def test_on_non_parsable_trashinfo(self):
        self.fs.write_file('/trash-dir/info/info_path.trashinfo',
                           '')

        trashed_files = list(self.trashed_files.all_trashed_files(None))

        assert {
                   'trashed_files': trashed_files,
                   'out': self.out.getvalue()} == {
                   'trashed_files': [],
                   'out': 'WARN: Non parsable trashinfo file: '
                          '/trash-dir/info/info_path.trashinfo, because '
                          'Unable to parse Path\n'
               }

    def test_on_io_error(self):
        self.fs.mkdir_p('/trash-dir/info/info_path.trashinfo')

        trashed_files = list(self.trashed_files.all_trashed_files(None))

        assert {
                   'trashed_files': trashed_files,
                   'out': self.out.getvalue()
               } == {
                   'trashed_files': [],
                   'out': "WARN: IOErrorReadingTrashInfo("
                          "path='/trash-dir/info/info_path.trashinfo', "
                          "error='Unable to read: "
                          "/trash-dir/info/info_path.trashinfo')\n"
               }
