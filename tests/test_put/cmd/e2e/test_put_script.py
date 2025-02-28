import pytest

from tests.support.run.run_command import run_command


@pytest.mark.slow
class TestRmScript:
    def test_trash_put_works(self):
        result = run_command('.', 'trash-put')
        assert ("usage: trash-put [OPTION]... FILE..." in
                result.stderr.splitlines())

    def test_trash_put_touch_filesystem(self):
        result = run_command('.', 'trash-put', ['non-existent'])
        assert ("trash-put: cannot trash non existent 'non-existent'\n" ==
                result.stderr)
