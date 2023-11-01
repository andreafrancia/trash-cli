# Copyright (C) 2008-2021 Andrea Francia Trivolzio(PV) Italy

import unittest

import pytest
from six import StringIO

from trashcli.fs import read_file
from trashcli.put.fs.real_fs import RealFs
from trashcli.put.janitor_tools.info_file_persister import TrashinfoData, \
    InfoFilePersister
from trashcli.put.my_logger import LogData, MyLogger
from trashcli.put.suffix import Suffix
from .support.fake_random import FakeRandomInt
from ..support.my_path import MyPath


@pytest.mark.slow
class TestPersistTrashInfo(unittest.TestCase):
    def setUp(self):
        self.path = MyPath.make_temp_dir()
        self.fs = RealFs()
        self.stderr = StringIO()
        self.logger = MyLogger(self.stderr)
        self.suffix = Suffix(FakeRandomInt([0,1]))
        self.info_dir = InfoFilePersister(self.fs, self.logger, self.suffix)

    def test_persist_trash_info_first_time(self):
        trash_info_file = self._persist_trash_info('dummy-path', b'content')

        assert self.path / 'dummy-path.trashinfo' == trash_info_file
        assert 'content' == read_file(trash_info_file)

    def test_persist_trash_info_first_100_times(self):
        self.test_persist_trash_info_first_time()

        trash_info_file = self._persist_trash_info('dummy-path',
                                                   b'content')

        assert self.path / 'dummy-path_1.trashinfo' == trash_info_file
        assert 'content' == read_file(trash_info_file)

    def tearDown(self):
        self.path.clean_up()

    def _persist_trash_info(self, basename, content):
        log_data = LogData('trash-cli', 2)
        data = TrashinfoData(basename, content, self.path)
        for result in self.info_dir.try_persist(data, log_data):
            if result is not None:
                return result.trashinfo_path
