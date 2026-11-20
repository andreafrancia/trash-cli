import errno
import os
import pytest

from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.support.fs_fixture import real_fs_fixture
from trashcli.fslib.real.real_atomic_write import RealAtomicWrite

fs = real_fs_fixture
temp_dir = temp_dir_fixture


@pytest.mark.slow
class TestAtomicWrite:
    @pytest.fixture(autouse=True)
    def setup_fs(self, fs, temp_dir):
        self.fs = fs
        self.temp_dir = temp_dir
        self.aw = RealAtomicWrite()

    def test_the_second_open_should_fail(self):
        path = self.temp_dir / "a"
        file_handle = self.aw.open_for_write_in_exclusive_and_create_mode(path)
        with pytest.raises(OSError) as e:
            self.aw.open_for_write_in_exclusive_and_create_mode(path)

        assert e.value.errno == errno.EEXIST
        os.close(file_handle)

    def test_short_filename(self):
        path = self.temp_dir / 'a'

        self.fs.atomic_write(path, b'contents')

        assert 'contents' == self.fs.read_file(path)

    def test_too_long_filename(self):
        path = self.temp_dir / ('a' * 2000)

        with pytest.raises(OSError) as e:
            self.fs.atomic_write(path, b'contents')
        assert e.value.errno == errno.ENAMETOOLONG

    def test_filename_already_taken(self):
        self.fs.atomic_write(self.temp_dir / "a", b'contents')

        with pytest.raises(OSError) as e:
            self.fs.atomic_write(self.temp_dir / "a", b'contents')
        assert e.value.errno == errno.EEXIST
