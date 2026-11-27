# Copyright (C) 2008-2021 Andrea Francia Trivolzio(PV) Italy
import pytest
from six import StringIO

from tests.support.fs_fixture import real_fs_fixture
from trashcli.put.janitor_tools.info_file_persister import InfoFilePersister
from trashcli.put.janitor_tools.info_file_persister import TrashinfoData
from trashcli.put.my_logger import LogData
from trashcli.put.my_logger import MyLogger
from trashcli.put.my_logger import StreamBackend
from trashcli.put.suffix import Suffix
from tests.support.put.fake_random import FakeRandomInt
from tests.support.dirs.temp_dir import temp_dir_fixture

fs = real_fs_fixture
temp_dir = temp_dir_fixture

@pytest.mark.slow
class TestPersistTrashInfo:
    @pytest.fixture(autouse=True)
    def setup(self, fs, temp_dir):
        self.fs = fs
        self.path = temp_dir
        self.stderr = StringIO()
        self.backend = StreamBackend(self.stderr)
        self.logger = MyLogger(self.backend)
        self.suffix = Suffix(FakeRandomInt([0, 1]))
        self.info_dir = InfoFilePersister(self.fs, self.logger, self.suffix)

    def test_persist_trash_info_first_time(self):
        trash_info_file = self._run_persist('dummy-path', b'content')

        assert self.path / 'dummy-path.trashinfo' == trash_info_file
        assert 'content' == self.fs.read_file(trash_info_file)

    def test_persist_trash_info_first_100_times(self):
        self.test_persist_trash_info_first_time()

        trash_info_file = self._run_persist('dummy-path',
                                                   b'content')

        assert self.path / 'dummy-path_1.trashinfo' == trash_info_file
        assert 'content' == self.fs.read_file(trash_info_file)

    def _run_persist(self, basename, content):
        log_data = LogData('trash-cli', 2)
        data = TrashinfoData(basename, content, self.path)
        return self.info_dir.persist(data, log_data).value().trashinfo_path
