import errno
import shutil

import pytest

from tests.support.dirs.temp_dir import make_temp_dir
from tests.support.fs_fixture import real_fs_fixture, fsx_fixture
from trashcli.fslib.protocols.fs import Fs

fs = real_fs_fixture
fsx = fsx_fixture

@pytest.mark.slow
class TestMakeUnreadableDir:
    @pytest.fixture(autouse=True)
    def setup_fs(self, fs, fsx):
        self.fsx = fsx
        self.tmp_dir = make_temp_dir(fs)
        self.unreadable_dir = self.tmp_dir / 'unreadable-dir'

        self.fsx.make_unreadable_dir(self.unreadable_dir)

    def test_the_directory_has_been_created(
            self, fs):  # type: (Fs) -> None
        assert fs.path_exists(self.unreadable_dir)

    def test_and_can_not_be_removed(self):
        with pytest.raises(OSError) as e:
            self.fsx.remove_file2(self.unreadable_dir)
        assert errno.errorcode[e.value.errno] == 'EACCES'

    def teardown_method(self):
        self.fsx.make_readable(self.unreadable_dir)
        shutil.rmtree(self.unreadable_dir)
