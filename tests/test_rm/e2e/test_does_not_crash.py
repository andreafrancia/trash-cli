import pytest

from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.support.fs_fixture import real_fs_fixture
from tests.support.run.run_command import run_command

fs = real_fs_fixture
temp_dir = temp_dir_fixture


class TestWithoutArguments:
    @pytest.fixture
    def run_trash_rm_without_arguments(self, temp_dir):
        return run_command(temp_dir, "trash-rm", [], env={
            'XDG_DATA_HOME': temp_dir / 'XDG_DATA_HOME',
            'TRASH_VOLUMES': ':',
        })

    def test_exit_code_is_8(self, run_trash_rm_without_arguments):
        assert run_trash_rm_without_arguments.exit_code == 8

    def test_stderr_shows_usage(self, run_trash_rm_without_arguments):
        assert run_trash_rm_without_arguments.stderr.startswith(
            "Usage:\n    trash-rm PATTERN\n\nPlease specify PATTERN.\n")

    def test_stdout_is_empty(self, run_trash_rm_without_arguments):
        assert run_trash_rm_without_arguments.stdout == ""
