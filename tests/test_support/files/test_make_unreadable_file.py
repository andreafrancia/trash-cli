import errno

import pytest

from tests.support.dirs.temp_dir import make_temp_dir, temp_dir_fixture
from tests.support.fs_fixture import real_fs_fixture, fsx_fixture

fs = real_fs_fixture
fsx = fsx_fixture
temp_dir = temp_dir_fixture


@pytest.mark.slow
class TestMakeUnreadableFile:

    def test(self, fs, temp_dir, fsx):
        path = temp_dir / "unreadable"
        fsx.make_unreadable_file(temp_dir / "unreadable")
        with pytest.raises((OSError, IOError)) as e:
            fs.read_file(path)

        assert errno.errorcode[e.value.errno] == 'EACCES'

