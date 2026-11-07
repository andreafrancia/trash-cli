import pytest

from tests.support.asserts import assert_starts_with
from tests.support.fakes.fake_trash_dir import FakeTrashDir
from tests.support.dirs.temp_dir import temp_dir_fixture_fs
from tests.support.fs_fixture import fake_fs_fixture
from tests.support.rm.rm_user import rm_user_fixture

fs = fake_fs_fixture
temp_dir = temp_dir_fixture_fs
user = rm_user_fixture


class TestTrashRmCmdRun:
    @pytest.fixture(autouse=True)
    def fake_trash_dir(self, xdg_data_home):
        return FakeTrashDir(xdg_data_home / 'Trash')

    @pytest.fixture
    def xdg_data_home(self, temp_dir):
        return temp_dir

    def test_without_arguments(self, user):
        user.run_rm([])

        assert_starts_with(
            user.stderr,
            'Usage:\n    trash-rm PATTERN\n\nPlease specify PATTERN.\n')

    def test_without_pattern_argument(self, user):
        user.add_volume('/vol1')

        user.run_rm([None])

        assert '' == user.stderr
