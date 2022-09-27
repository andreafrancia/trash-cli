import unittest
from typing import cast

from six import StringIO

from mock import Mock
from datetime import datetime

from trashcli.put.trash_directories_finder import TrashDirectoriesFinder
from trashcli.put.file_trasher import FileTrasher
from trashcli.put.trash_put_cmd import MyLogger, TrashResult, TrashPutReporter
import os


class TestFileTrasher(unittest.TestCase):
    def setUp(self):
        self.reporter = Mock()
        self.fs = Mock()
        self.volumes = Mock()

        trash_directories_finder = Mock(spec=['possible_trash_directories_for'])
        trash_directories_finder.possible_trash_directories_for.return_value = []

        self.environ = {'XDG_DATA_HOME': '/xdh'}
        trash_directories_finder = TrashDirectoriesFinder(1001, self.volumes)
        self.file_trasher = FileTrasher(self.fs,
                                        self.volumes,
                                        lambda x: x,
                                        datetime.now,
                                        trash_directories_finder,
                                        os.path.dirname)
        self.logger = cast(MyLogger, Mock())

    def test_log_volume(self):
        self.volumes.volume_of.return_value = '/'

        result = TrashResult(False)
        self.file_trasher.trash_file('a-dir/with-a-file',
                                     False,
                                     None,
                                     result,
                                     self.logger,
                                     cast(TrashPutReporter, self.reporter),
                                     {})

        self.reporter.volume_of_file.assert_called_with('/')

    def test_should_report_when_trash_fail(self):
        self.volumes.volume_of.return_value = '/'
        self.fs.move.side_effect = IOError

        result = TrashResult(False)
        self.file_trasher.trash_file('non-existent',
                                     None,
                                     None,
                                     result,
                                     self.logger,
                                     cast(TrashPutReporter, self.reporter),
                                     {})

        self.reporter.unable_to_trash_file.assert_called_with('non-existent')

    def test_when_path_does_not_exists(self):
        self.volumes.volume_of.return_value = '/disk'
        stderr = StringIO()
        verbose_level = 2
        logger = MyLogger(stderr, "trash-put", verbose_level)
        reporter = TrashPutReporter(logger, {})
        result = TrashResult(False)

        self.file_trasher.trash_file("non-existent", None, None, result, logger,
                                     reporter, self.environ)

        assert stderr.getvalue().splitlines() == [
            'trash-put: Volume of file: /disk',
            'trash-put: Trash-dir: /xdh/Trash from volume: /disk',
            'trash-put: .trashinfo created as /xdh/Trash/info/non-existent.trashinfo.',
            "trash-put: 'non-existent' trashed in /xdh/Trash"]
