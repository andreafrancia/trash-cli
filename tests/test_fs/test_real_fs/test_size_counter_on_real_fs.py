import pytest

from trashcli.put.fs.size_counter import SizeCounter
from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.support.fs_fixture import real_fs_fixture

fs = real_fs_fixture
temp_dir = temp_dir_fixture


@pytest.mark.slow
class TestSizeCounterOnRealFs:
    @pytest.fixture(autouse=True)
    def setup_fs(self, fs, temp_dir):
        self.fs = fs
        self.tmp_dir = temp_dir
        self.counter = SizeCounter(self.fs)

    def test_a_single_file(self):
        self.fs.write_file(self.tmp_dir / 'file', 10 * 'a')

        assert self.counter.get_size_recursive(self.tmp_dir / 'file') == 10

    def test_two_files(self):
        self.fs.write_file(self.tmp_dir / 'a', 100 * 'a')
        self.fs.write_file(self.tmp_dir / 'b', 23 * 'b')

        assert self.counter.get_size_recursive(self.tmp_dir) == 123

    def test_recursive(self):
        self.fs.write_file(self.tmp_dir / 'a', 3 * '-')
        self.fs.makedirs(self.tmp_dir / 'dir', 0o777)
        self.fs.write_file(self.tmp_dir / 'dir' / 'a', 20 * '-')
        self.fs.makedirs(self.tmp_dir / 'dir' / 'dir', 0o777)
        self.fs.write_file(self.tmp_dir / 'dir' / 'dir' / 'b', 100 * '-')

        assert self.counter.get_size_recursive(self.tmp_dir) == 123

