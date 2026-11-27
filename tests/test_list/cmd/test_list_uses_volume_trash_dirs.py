# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy
import pytest

from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.support.fs_fixture import real_fs_fixture
from tests.test_list.cmd.support.trash_list_user import TrashListUser
from tests.test_list.cmd.support.trash_list_user import trash_list_user

fs = real_fs_fixture
user = trash_list_user
temp_dir = temp_dir_fixture

class TestListUsesVolumeTrashDirs:
    @pytest.fixture
    def user(self, user):
        user.set_fake_uid(123)
        user.add_disk("disk")
        return user

    def test_it_should_lists_content_from_method_1_trash_dir(
            self, user):  # type: (TrashListUser) -> None
        user.trash_dir1("disk").make_parent_sticky()
        user.trash_dir1("disk").add_trashinfo4('file', "2000-01-01")

        result = user.run_trash_list()

        assert result.stdout == "2000-01-01 00:00:00 /disk/file\n"

    def test_it_should_lists_content_from_method_2_trash_dir(self, user):
        user.trash_dir2("disk").add_trashinfo4('file', "2000-01-01")

        result = user.run_trash_list()

        assert result.stdout == "2000-01-01 00:00:00 /disk/file\n"
