import pytest

from tests.run_command import run_commmand
from tests.run_command import temp_dir
from trashcli.put.fs.real_fs import RealFs

fs = RealFs()

temp_dir = temp_dir


@pytest.mark.slow
class TestTrashPutTrivial:
    def test_trash_put_works(self):
        result = run_commmand('.', 'trash-put')
        assert ("usage: trash-put [OPTION]... FILE..." in
                result.stderr.splitlines())

    def test_trash_put_touch_filesystem(self):
        result = run_commmand('.', 'trash-put', ['non-existent'])
        assert (result.stderr ==
                "trash-put: cannot trash non existent 'non-existent'\n")

