import datetime
import unittest
from typing import List
from typing import NamedTuple

from six import StringIO

from tests.support.put.fake_fs.fake_fs import FakeFs
from tests.support.restore.logger.fake_logger import FakeLogger
from trashcli.fstab.volumes import FakeVolumes
from trashcli.restore.info_dir_searcher import InfoDirSearcher
from trashcli.restore.trash_directories import TrashDirectoriesImpl
from trashcli.restore.trashed_file import TrashedFile
from trashcli.restore.trashed_files import TrashedFiles


class TestTrashedFiles(unittest.TestCase):
    def setUp(self):
        self.fs = FakeFs()
        self.fs.mkdir_p("/trash-dir/info")

    def test(self):
        self.fs.write_file('/trash-dir/info/info_path.trashinfo',
                           b'Path=name\n'
                           b'DeletionDate=2001-01-01T10:10:10')

        result = self.list_trashed_files()

        assert result == Result(
            [
                TrashedFile('/name',
                            datetime.datetime(2001, 1, 1,
                                              10, 10,
                                              10),
                            '/trash-dir/info/info_path.trashinfo',
                            '/trash-dir/files/info_path'),
            ],
            ''
        )

    def test_on_non_trashinfo(self):
        self.fs.touch('/trash-dir/info/info_path.non-trashinfo')

        result = self.list_trashed_files()

        assert result == Result(
            [],
            'WARN: Non .trashinfo file in info dir\n'
        )

    def test_on_non_parsable_trashinfo(self):
        self.fs.write_file('/trash-dir/info/info_path.trashinfo',
                           b'')

        result = self.list_trashed_files()

        assert result == Result(
            [],
            'WARN: Non parsable trashinfo file: '
            '/trash-dir/info/info_path.trashinfo, because '
            'Unable to parse Path\n'
        )

    def test_on_io_error(self):
        self.fs.mkdir_p('/trash-dir/info/info_path.trashinfo')

        result = self.list_trashed_files()

        assert result == Result(
            [],
            "WARN: IOErrorReadingTrashInfo("
            "path='/trash-dir/info/info_path.trashinfo', "
            "error='Unable to read: "
            "/trash-dir/info/info_path.trashinfo')\n")

    def list_trashed_files(self):
        out = StringIO()
        logger = FakeLogger(out)

        fs = self.fs

        volumes = FakeVolumes([])
        trashed_files = TrashedFiles(volumes, 123, {}, self.fs,
                                     logger)

        trashed_files_list = list(trashed_files.all_trashed_files("/trash-dir"))
        return Result(
            trashed_files_list,
            out.getvalue()
        )


class Result(NamedTuple("Result", [
    ('trashed_files', List[TrashedFile]),
    ('out', str)
])):
    pass
