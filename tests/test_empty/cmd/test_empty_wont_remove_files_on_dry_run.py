# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import pytest

from tests.support.empty.empty_user import empty_user_fixture, EmptyUser
from tests.support.fs_fixture import fake_fs_fixture
from tests.support.trash_dirs.given_trash import GivenTrash
from trashcli.fslib.protocols.fs import Fs

user = empty_user_fixture
fs = fake_fs_fixture


class TestEmptyWontRemoveFilesOnDryRun:
    @pytest.fixture(autouse=True, scope="function")
    def set_up_trashed_file(self, fs):
        self.trash = GivenTrash(fs)
        self.environ = {'XDG_DATA_HOME': '/xdg'}
        self.trash.has_file('/xdg/Trash/info/pippo.trashinfo')
        self.trash.has_file('/xdg/Trash/files/pippo')

    def test(self,
             user,  # type: EmptyUser
             fs,  # type: Fs
             ):
        user.run_empty(environ=self.environ)

        assert fs.listdir('/xdg/Trash/files') == []
        assert fs.listdir('/xdg/Trash/info') == []

    def test_with_dry_run(self, user, fs):
        user.run_empty(['--dry-run'], self.environ)

        assert fs.listdir('/xdg/Trash/files') == ['pippo']
        assert fs.listdir('/xdg/Trash/info') == ['pippo.trashinfo']
        assert user.stdout == \
               'would remove /xdg/Trash/files/pippo\n' \
               'would remove /xdg/Trash/info/pippo.trashinfo\n'
