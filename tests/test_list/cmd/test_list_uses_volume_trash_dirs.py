# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy
import pytest

from tests.test_list.cmd.support.trash_list_user import trash_list_user  # noqa


class TestListUsesVolumeTrashDirs:
    @pytest.fixture
    def user(self, trash_list_user):
        u = trash_list_user
        u.set_fake_uid(123)
        u.add_disk("disk")
        return u

    def test_it_should_lists_content_from_method_1_trash_dir(self, user):
        user.trash_dir1("disk").make_parent_sticky()
        user.trash_dir1("disk").add_trashinfo4('file', "2000-01-01")

        result = user.run_trash_list()

        assert result.stdout == "2000-01-01 00:00:00 /disk/file\n"

    def test_it_should_lists_content_from_method_2_trash_dir(self, user):
        user.trash_dir2("disk").add_trashinfo4('file', "2000-01-01")

        result = user.run_trash_list()

        assert result.stdout == "2000-01-01 00:00:00 /disk/file\n"
