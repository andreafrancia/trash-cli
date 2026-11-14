import os

import pytest

from tests.support.put.my_file_not_found_error import MyFileNotFoundError
from trashcli.fslib.force_remover import ForceRemover
from trashcli.fslib.real.real_fs import RealFs

@pytest.mark.slow
class TestForceRemoverOnRealFs:
    def test_remove_file_fails_when_file_does_not_exists(self):
        file_remove2 = ForceRemover(RealFs(), {}, os.geteuid)
        with pytest.raises(MyFileNotFoundError):
            file_remove2.remove_path_forcefully('/non/existing/path')
