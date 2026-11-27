import pytest

from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.support.fs_fixture import real_fs_fixture
from tests.test_put.cmd.e2e.run_trash_put import run_trash_put
from trashcli.lib.exit_codes import EX_IOERR

fs = real_fs_fixture
temp_dir = temp_dir_fixture

@pytest.mark.slow
class TestOnNonExistentFile:
    def test_fails(self, temp_dir):
        result = run_trash_put(temp_dir, ['non-existent'])
        assert (result.combined() ==
                ["trash-put: cannot trash non existent 'non-existent'\n",
                 EX_IOERR])
