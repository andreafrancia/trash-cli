import errno

import pytest

from trashcli.rm.real_remover_fs import RealRemoverFs
from tests.support.fs_fixture import real_fs_fixture, fsx_fixture
from tests.support.dirs.temp_dir import temp_dir_fixture

fs = real_fs_fixture
temp_dir = temp_dir_fixture
fsx = fsx_fixture

@pytest.mark.slow
class TestFileRemover:
    def test_remove_file_fails_when_file_does_not_exists(
            self, fs):
        file_remover = RealRemoverFs(fs)
        with pytest.raises(OSError) as e:
            file_remover.remove_file2('/non/existing/path')

        assert e.value.errno == errno.ENOENT
