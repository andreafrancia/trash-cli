import pytest

from tests.support.asserts import assert_starts_with
from tests.support.fs_fixture import fake_fs_fixture
from tests.support.rm.rm_user import rm_user_fixture

fs = fake_fs_fixture
user = rm_user_fixture


class TestTrashRmCmdRun:
    def test_without_arguments(self, user):
        user.run_rm([])

        assert_starts_with(
            user.stderr,
            'Usage:\n    trash-rm PATTERN\n\nPlease specify PATTERN.\n')

    def test_without_pattern_argument(self, user):
        user.add_volume('/vol1')

        user.run_rm([None])

        assert '' == user.stderr
