import pytest

from tests.run_command import run_trash_put_in_tmp_dir
from tests.run_command import temp_dir  # noqa
from trashcli.lib.exit_codes import EX_IOERR


@pytest.mark.slow
class TestOnNonExistentFile:
    def test_fails(self, temp_dir):
        result = run_trash_put_in_tmp_dir(temp_dir, ['non-existent'])
        assert (result.combined() ==
                ["trash-put: cannot trash non existent 'non-existent'\n",
                 EX_IOERR])
