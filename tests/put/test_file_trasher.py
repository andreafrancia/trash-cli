import os
import unittest
from datetime import datetime

import flexmock
from six import StringIO

from mock import Mock
from trashcli.put.trash_file_in import TrashFileIn
from typing import cast
from trashcli.put.file_trasher import FileTrasher
from trashcli.put.my_logger import MyLogger
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
        parent_path = os.path.dirname
        self.suffix = Mock(spec=Suffix)
        self.suffix.suffix_for_index.return_value = '_suffix'
        self.trash_dir = flexmock.Mock(spec=TrashDirectoryForPut)
        self.trash_file_in = flexmock.Mock(spec=TrashFileIn)
        self.file_trasher = FileTrasher(self.volumes,
                                        datetime.now,
                                        trash_directories_finder,
                                        parent_path,
                                        self.logger,
                                        self.reporter,
                                        cast(TrashFileIn, self.trash_file_in))


    def test_should_report_when_trash_fail(self):
        self.volumes.volume_of.return_value = '/'
        flexmock.flexmock(self.trash_file_in).should_receive('trash_file_in'). \
            and_return(False)

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

    def test_when_trash_file_in_fails(self):
        self.volumes.volume_of.return_value = '/disk'
        result = TrashResult(False)
        flexmock.flexmock(self.trash_file_in).should_receive('trash_file_in'). \
            and_return(False)

        self.file_trasher.trash_file("non-existent",
                                     None,
                                     None,
                                     result,
                                     self.environ,
                                     1001,
                                     'trash-put',
                                     99)

        assert self.stderr.getvalue().splitlines() == [
            'trash-put: volume of file: /disk',
            "trash-put: cannot trash non existent 'non-existent'"]
