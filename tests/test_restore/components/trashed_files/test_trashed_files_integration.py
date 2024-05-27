import datetime
import unittest

from tests.support.py2mock import Mock
from six import StringIO

from tests.support.dirs.my_path import MyPath
from tests.support.fs_fixture import FsFixture
from tests.support.restore.logger.fake_logger import FakeLogger
from trashcli.fstab.volumes import FakeVolumes
from trashcli.put.fs.real_fs import RealFs
from trashcli.restore.trashed_files import TrashedFiles


class TestTrashedFilesIntegration(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        volumes = FakeVolumes([self.tmp_dir / 'volume'])
        self.fs = RealFs()
        logger = FakeLogger(StringIO())
        self.trashed_files = TrashedFiles(volumes, 123, {},
                                               self.fs, logger)
        self.fx = FsFixture(self.fs)
        self.trash_dir = self.tmp_dir / 'volume' / '.Trash/123'


    def test(self):
        self.fx.require_empty_dir(self.trash_dir / 'info')
        self.fx.make_file(self.trash_dir / 'info/info_path.trashinfo',
                          b'Path=name\nDeletionDate=2001-01-01T10:10:10')

        trashed_files = list(self.trashed_files.all_trashed_files(None))

        trashed_file = trashed_files[0]
        assert self.tmp_dir / 'volume/name' == trashed_file.original_location
        assert (datetime.datetime(2001, 1, 1, 10, 10, 10) ==
                trashed_file.deletion_date)
        assert self.trash_dir / 'info/info_path.trashinfo' == trashed_file.info_file
        assert self.trash_dir / 'files/info_path' == trashed_file.original_file

    def tearDown(self):
        self.tmp_dir.clean_up()
