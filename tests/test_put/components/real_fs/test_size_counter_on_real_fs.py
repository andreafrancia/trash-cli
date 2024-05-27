import pytest

from tests.support.dirs.temp_dir import temp_dir
from trashcli.put.fs.real_fs import RealFs
from trashcli.put.fs.size_counter import SizeCounter

temp_dir = temp_dir


@pytest.mark.slow
class TestSizeCounterOnRealFs:
    @pytest.fixture
    def counter(self, fs):
        return SizeCounter(fs)

    @pytest.fixture
    def fs(self, temp_dir):
        return RealFs()

    def test_a_single_file(self, fs, counter, temp_dir):
        fs.make_file(temp_dir / 'file', 10 * b'a')

        assert counter.get_size_recursive(temp_dir / 'file') == 10

    def test_two_files(self, fs, counter, temp_dir):
        fs.make_file(temp_dir / 'a', 100 * b'a')
        fs.make_file(temp_dir / 'b', 23 * b'b')

        assert counter.get_size_recursive(temp_dir) == 123

    def test_recursive(self, fs, counter, temp_dir):
        fs.make_file_p(temp_dir / 'a', 3 * b'-')
        fs.make_file_p(temp_dir / 'dir' / 'a', 20 * b'-')
        fs.make_file_p(temp_dir / 'dir' / 'dir' / 'b', 100 * b'-')

        assert counter.get_size_recursive(temp_dir) == 123
