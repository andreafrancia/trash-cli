# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy
import pytest

from tests.test_list.cmd.support.trash_list_user import trash_list_user  # noqa


class TestAlternateTrashDir:
    @pytest.fixture
    def user(self, trash_list_user):
        u = trash_list_user
        u.set_fake_uid(123)
        u.add_disk("disk")
        return u

    def test_should_list_contents_of_alternate_trashdir(self, user):
        user.trash_dir2("disk").add_trashinfo4('file', "2000-01-01")

        output = user.run_trash_list()

        assert output.stdout == "2000-01-01 00:00:00 /disk/file\n"
