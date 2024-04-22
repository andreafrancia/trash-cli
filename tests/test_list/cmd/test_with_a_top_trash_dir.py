# Copyright (C) 2011-2024 Andrea Francia Trivolzio(PV) Italy
import pytest

from tests.test_list.cmd.support.trash_list_user import trash_list_user  # noqa


class TestWithATopTrashDir:
    @pytest.fixture
    def user(self, trash_list_user):
        u = trash_list_user
        u.set_fake_uid(123)
        u.add_disk("topdir")
        return u

    def test_should_list_its_contents_if_parent_is_sticky(self, user):
        user.trash_dir1("topdir").make_parent_sticky()
        user.trash_dir1("topdir").add_a_valid_trashinfo()

        output = user.run_trash_list()

        assert output.whole_output() == "2000-01-01 00:00:00 /topdir/file1\n"

    def test_and_should_warn_if_parent_is_not_sticky(self, user):
        user.trash_dir1("topdir").make_parent_unsticky()
        user.trash_dir1("topdir").make_dir()

        output = user.run_trash_list()

        assert output.whole_output() == (
            "TrashDir skipped because parent not sticky: /topdir/.Trash/123\n")

    def test_but_it_should_not_warn_when_the_parent_is_unsticky_but_there_is_no_trashdir(
            self, user):
        user.trash_dir1("topdir").make_parent_unsticky()
        user.trash_dir1("topdir").does_not_exist()

        output = user.run_trash_list()

        assert output.whole_output() == ''

    def test_should_ignore_trash_from_a_unsticky_topdir(self, user):
        user.trash_dir1("topdir").make_parent_unsticky()
        user.trash_dir1("topdir").add_a_valid_trashinfo()

        output = user.run_trash_list()

        assert output.whole_output() == (
            'TrashDir skipped because parent not sticky: /topdir/.Trash/123\n')

    def test_it_should_skip_a_symlink(self, user):
        user.trash_dir1("topdir").make_parent_symlink()
        user.trash_dir1("topdir").add_a_valid_trashinfo()

        output = user.run_trash_list()

        assert output.err_and_out() == (
            'TrashDir skipped because parent not sticky: /topdir/.Trash/123\n',
            '')
