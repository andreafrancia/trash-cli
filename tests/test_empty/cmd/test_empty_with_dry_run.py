# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import pytest

from tests.support.empty.empty_user import empty_user_fixture
from tests.support.fs_fixture import fake_fs_fixture
from tests.support.trash_dirs.given_trash import GivenTrash

fs = fake_fs_fixture
user = empty_user_fixture

class TestEmptyWithDryRun:
    @pytest.fixture
    def trash(self, fs):
        return GivenTrash(fs)

    @pytest.fixture(autouse=True, scope="function")
    def setup_trash(self, user, trash):
        user.add_environ('XDG_DATA_HOME', '/xdg')
        trash.has_file('/xdg/Trash/info/pippo.trashinfo')
        trash.has_file('/xdg/Trash/files/pippo')

    def test(self, fs, user):
        user.run_empty([])

        assert fs.listdir('/xdg/Trash/files') == []
        assert fs.listdir('/xdg/Trash/info') == []

    def test_with_dry_run(self, fs, user):
        user.run_empty(['--dry-run'])

        assert fs.listdir('/xdg/Trash/files') == ['pippo']
        assert fs.listdir('/xdg/Trash/info') == ['pippo.trashinfo']
        assert user.stdout == \
               'would remove /xdg/Trash/files/pippo\n' \
               'would remove /xdg/Trash/info/pippo.trashinfo\n'
