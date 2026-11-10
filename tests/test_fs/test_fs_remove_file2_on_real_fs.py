import os

import pytest

from tests.support.put.my_file_not_found_error import MyFileNotFoundError
from trashcli.fslib.fs_remove_file2 import FsRemoveFile2
from trashcli.fslib.real.real_fs import RealFs

@pytest.mark.slow
class TestFsRemoveFile2OnRealFs:
    def test_remove_file_fails_when_file_does_not_exists(self):
        file_remove2 = FsRemoveFile2(RealFs(), {}, os.geteuid)
        with pytest.raises(MyFileNotFoundError):
            file_remove2.remove_file2('/non/existing/path')
