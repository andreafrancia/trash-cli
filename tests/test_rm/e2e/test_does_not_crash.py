import pytest

from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.support.fs_fixture import real_fs_fixture
from tests.support.run.run_command import run_command

fs = real_fs_fixture
temp_dir = temp_dir_fixture


class TestDoesNotCrash:
    @pytest.fixture(autouse=True)
    def run_trash_rm_version(self, temp_dir):
        return run_command(temp_dir, "trash-rm", [])

    def test_exit_code__is_not_zeros(self, run_trash_rm_version):
        assert run_trash_rm_version.exit_code == 8

    def test_stderr__should_contains_usage(self, run_trash_rm_version):
        assert run_trash_rm_version.stderr.startswith("Usage")

    def test_stdout__should_be_empty(self, run_trash_rm_version):
        assert run_trash_rm_version.stdout == ""
