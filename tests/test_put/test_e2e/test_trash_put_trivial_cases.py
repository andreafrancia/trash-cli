import pytest

from tests.run_command import run_command
from tests.run_command import temp_dir  # noqa
from trashcli.put.fs.real_fs import RealFs

fs = RealFs()


@pytest.mark.slow
class TestTrashPutTrivial:
    def test_trash_put_touch_filesystem(self, temp_dir):
        result = run_command('.', 'trash-put', ['non-existent'])
        assert (result.stderr ==
                "trash-put: cannot trash non existent 'non-existent'\n")
