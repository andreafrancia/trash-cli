# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import pytest

from tests.support.dirs.temp_dir import temp_dir_fixture_fs
from tests.support.empty.empty_user import empty_user_fixture
from tests.support.fs_fixture import real_fs_fixture
from tests.support.trash_dirs.given_trash import GivenTrash

fs = real_fs_fixture
user = empty_user_fixture
temp_dir = temp_dir_fixture_fs

@pytest.mark.slow
class TestTrashEmptyWtihDryRunOnRealFs:
    @pytest.fixture
    def trash(self, fs):
        return GivenTrash(fs)

    @pytest.fixture(autouse=True, scope="function")
    def setup_trash(self, temp_dir, trash):
        self.xdg = temp_dir / 'xdg'
        self.environ = {'XDG_DATA_HOME': self.xdg}
        trash.has_file(self.xdg / 'Trash/info/pippo.trashinfo', '')
        trash.has_file(self.xdg / 'Trash/files/pippo', '')

    def test(self, fs, user):
        user.run_empty([], self.environ)

        assert fs.listdir(self.xdg / 'Trash/files') == []
        assert fs.listdir(self.xdg / 'Trash/info') == []

    def test_with_dry_run(self, fs, user):
        user.run_empty(['--dry-run'], self.environ)

        assert fs.listdir(self.xdg / 'Trash/files') == ['pippo']
        assert fs.listdir(self.xdg / 'Trash/info') == ['pippo.trashinfo']
        assert user.stdout == \
               'would remove %s/Trash/files/pippo\n' \
               'would remove %s/Trash/info/pippo.trashinfo\n' % (
                   self.xdg, self.xdg)
