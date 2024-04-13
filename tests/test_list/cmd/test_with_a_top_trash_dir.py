# Copyright (C) 2011-2024 Andrea Francia Trivolzio(PV) Italy

import os

from tests.support.asserts import assert_equals_with_unidiff
from tests.support.files import make_empty_dir
from tests.support.files import make_sticky_dir
from tests.support.files import make_unsticky_dir
from tests.support.my_path import MyPath
from tests.test_list.cmd.support.trash_list_user import TrashListUser


class TestWithATopTrashDir:
    def setup_method(self):
        self.temp_dir = MyPath.make_temp_dir()
        self.top_dir = self.temp_dir / "topdir"
        make_empty_dir(self.top_dir)
        self.user = TrashListUser(MyPath.make_temp_dir())
        self.user.set_fake_uid(123)
        self.user.add_volume(self.top_dir)

    def test_should_list_its_contents_if_parent_is_sticky(self):
        make_sticky_dir(self.top_dir / '.Trash')
        self.user.top1(self.top_dir).add_a_valid_trashinfo()

        output = self.user.run_trash_list()

        assert_equals_with_unidiff(
            "2000-01-01 00:00:00 %s/file1\n" % self.top_dir,
            output.whole_output())

    def test_and_should_warn_if_parent_is_not_sticky(self):
        make_unsticky_dir(self.top_dir / '.Trash')
        os.mkdir(self.top_dir / '.Trash' / '123')

        output = self.user.run_trash_list()

        assert_equals_with_unidiff(
            "TrashDir skipped because parent not sticky: %s/.Trash/123\n" %
            self.top_dir,
            output.whole_output()
        )

    def test_but_it_should_not_warn_when_the_parent_is_unsticky_but_there_is_no_trashdir(
            self):
        make_unsticky_dir(self.top_dir / '.Trash')
        but_does_not_exists_any(self.top_dir / '.Trash/123')

        output = self.user.run_trash_list()

        assert_equals_with_unidiff("", output.whole_output())

    def test_should_ignore_trash_from_a_unsticky_topdir(self):
        make_unsticky_dir(self.top_dir / '.Trash')
        self.user.top1(self.top_dir).add_a_valid_trashinfo()

        output = self.user.run_trash_list()

        assert_equals_with_unidiff('', output.stdout)

    def test_it_should_ignore_Trash_is_a_symlink(self):
        when_is_a_symlink_to_a_dir(self.top_dir / '.Trash')
        self.user.top1(self.top_dir).add_a_valid_trashinfo()

        output = self.user.run_trash_list()

        assert_equals_with_unidiff('', output.stdout)

    def test_and_should_warn_about_it(self):
        when_is_a_symlink_to_a_dir(self.top_dir / '.Trash')
        self.user.top1(self.top_dir).add_a_valid_trashinfo()

        output = self.user.run_trash_list()

        assert_equals_with_unidiff(
            'TrashDir skipped because parent not sticky: %s/.Trash/123\n' %
            self.top_dir,
            output.whole_output()
        )


def but_does_not_exists_any(path):
    assert not os.path.exists(path)


def when_is_a_symlink_to_a_dir(path):
    dest = "%s-dest" % path
    os.mkdir(dest)
    rel_dest = os.path.basename(dest)
    os.symlink(rel_dest, path)
