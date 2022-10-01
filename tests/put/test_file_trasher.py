import os
import unittest
from datetime import datetime

from mock import Mock
from six import StringIO

from trashcli.put.file_trasher import FileTrasher, TrashFileIn
from trashcli.put.info_dir import InfoDir
from trashcli.put.my_logger import MyLogger
from trashcli.put.original_location import OriginalLocation, parent_realpath
from trashcli.put.path_maker import PathMaker
from trashcli.put.reporter import TrashPutReporter
from trashcli.put.suffix import Suffix
from trashcli.put.trash_directories_finder import TrashDirectoriesFinder
from trashcli.put.trash_directory_for_put import TrashDirectoryForPut
from trashcli.put.trash_result import TrashResult


class TestFileTrasher(unittest.TestCase):
    def setUp(self):
        self.reporter = Mock()
        self.fs = Mock()
        self.volumes = Mock()

        trash_directories_finder = Mock(spec=['possible_trash_directories_for'])
        trash_directories_finder.possible_trash_directories_for.return_value = []

        self.environ = {'XDG_DATA_HOME': '/xdh'}
        trash_directories_finder = TrashDirectoriesFinder(self.volumes)
        self.stderr = StringIO()
        self.logger = MyLogger(self.stderr)
        self.reporter = TrashPutReporter(self.logger)
        realpath = lambda x: x
        parent_path = os.path.dirname
        self.suffix = Mock(spec=Suffix)
        self.suffix.suffix_for_index.return_value = '_suffix'
        info_dir = InfoDir(self.fs, self.logger, self.suffix)
        original_location = OriginalLocation(parent_realpath)
        self.trash_dir = TrashDirectoryForPut(self.fs,
                                              PathMaker(),
                                              info_dir,
                                              original_location)
        self.trash_file_in = TrashFileIn(self.fs,
                                         realpath,
                                         self.volumes,
                                         datetime.now,
                                         parent_path,
                                         self.reporter,
                                         info_dir,
                                         self.trash_dir)
        self.file_trasher = FileTrasher(self.fs,
                                        self.volumes,
                                        realpath,
                                        datetime.now,
                                        trash_directories_finder,
                                        parent_path,
                                        self.logger,
                                        self.reporter,
                                        self.trash_file_in)

    def test_log_volume(self):
        self.volumes.volume_of.return_value = '/'
        result = TrashResult(False)
        self.file_trasher.trash_file('a-dir/with-a-file',
                                     False,
                                     None,
                                     result,
                                     {},
                                     1001,
                                     'trash-put',
                                     99)

        assert 'trash-put: Volume of file: /' in \
               self.stderr.getvalue().splitlines()

    def test_should_report_when_trash_fail(self):
        self.volumes.volume_of.return_value = '/'
        self.fs.move.side_effect = IOError

        result = TrashResult(False)
        self.file_trasher.trash_file('non-existent',
                                     None,
                                     None,
                                     result,
                                     {},
                                     1001,
                                     'trash-put',
                                     99)

        assert "trash-put: cannot trash non existent 'non-existent'" in \
               self.stderr.getvalue().splitlines()

    def test_when_path_does_not_exists(self):
        self.volumes.volume_of.return_value = '/disk'
        result = TrashResult(False)

        self.file_trasher.trash_file("non-existent",
                                     None,
                                     None,
                                     result,
                                     self.environ,
                                     1001,
                                     'trash-put',
                                     99)

        assert self.stderr.getvalue().splitlines() == [
            'trash-put: Volume of file: /disk',
            'trash-put: Trash-dir: /xdh/Trash from volume: /disk',
            'trash-put: .trashinfo created as /xdh/Trash/info/non-existent_suffix.trashinfo.',
            "trash-put: 'non-existent' trashed in /xdh/Trash"]
