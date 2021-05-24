import unittest

from mock import Mock
from datetime import datetime

from trashcli.put import TrashResult, Trasher, FileTrasher
import os


class TestFileTrasher(unittest.TestCase):
    def setUp(self):
        self.reporter = Mock()
        self.fs = Mock()
        self.volumes = Mock()
        self.volumes.volume_of.return_value = '/'

        trash_directories_finder = Mock(spec=['possible_trash_directories_for'])
        trash_directories_finder.possible_trash_directories_for.return_value = []
        self.file_trasher = FileTrasher(self.fs,
                                        self.volumes,
                                        lambda x: x,
                                        datetime.now,
                                        trash_directories_finder,
                                        os.path.dirname)
        self.logger = Mock()
        self.ignore_missing = False

    def test_log_volume(self):
        result = TrashResult(False)
        self.file_trasher.trash_file('a-dir/with-a-file',
                                     False,
                                     None,
                                     result,
                                     self.logger,
                                     self.reporter)

        self.reporter.volume_of_file.assert_called_with('/')

    def test_should_report_when_trash_fail(self):
        self.fs.move.side_effect = IOError

        result = TrashResult(False)
        self.file_trasher.trash_file('non-existent',
                                     None,
                                     None,
                                     result,
                                     self.logger,
                                     self.reporter)

        self.reporter.unable_to_trash_file.assert_called_with('non-existent')
