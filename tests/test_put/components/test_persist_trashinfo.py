# Copyright (C) 2008-2021 Andrea Francia Trivolzio(PV) Italy

import unittest

import pytest
from six import StringIO

from tests.support.dirs.my_path import MyPath
from tests.support.put.fake_random import FakeRandomInt
from trashcli.put.fs.real_fs import RealFs
from trashcli.put.janitor_tools.info_file_persister import InfoFilePersister
from trashcli.put.janitor_tools.info_file_persister import TrashinfoData
from trashcli.put.my_logger import LogData
from trashcli.put.my_logger import MyLogger
from trashcli.put.my_logger import StreamBackend
from trashcli.put.suffix import Suffix


@pytest.mark.slow
class TestPersistTrashInfo(unittest.TestCase):
    def setUp(self):
        self.path = MyPath.make_temp_dir()
        self.fs = RealFs()
        self.stderr = StringIO()
        self.backend = StreamBackend(self.stderr)
        self.logger = MyLogger(self.backend)
        self.suffix = Suffix(FakeRandomInt([0,1]))
        self.info_dir = InfoFilePersister(self.fs, self.logger, self.suffix)

    def test_persist_trash_info_first_time(self):
        trash_info_file = self._persist_trash_info('dummy-path', b'content')

        assert self.path / 'dummy-path.trashinfo' == trash_info_file
        assert b'content' == self.fs.read_file(trash_info_file)

    def test_persist_trash_info_first_100_times(self):
        self.test_persist_trash_info_first_time()

        trash_info_file = self._persist_trash_info('dummy-path',
                                                   b'content')

        assert self.path / 'dummy-path_1.trashinfo' == trash_info_file
        assert b'content' == self.fs.read_file(trash_info_file)

    def tearDown(self):
        self.path.clean_up()

    def _persist_trash_info(self, basename, content):
        log_data = LogData('trash-cli', 2)
        data = TrashinfoData(basename, content, self.path)
        return self.info_dir.create_trashinfo_file(data, log_data).trashinfo_path
