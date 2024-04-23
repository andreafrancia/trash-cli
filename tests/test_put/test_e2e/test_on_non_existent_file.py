import pytest

from tests.test_put.test_e2e.run_trash_put import run_trash_put
from tests.test_put.test_e2e.test_end_to_end_put import temp_dir
from trashcli.lib.exit_codes import EX_IOERR

temp_dir = temp_dir

@pytest.mark.slow
class TestOnNonExistentFile:
    def test_fails(self, temp_dir):
        result = run_trash_put(temp_dir, ['non-existent'])
        assert (result.combined() ==
                ["trash-put: cannot trash non existent 'non-existent'\n",
                 EX_IOERR])
