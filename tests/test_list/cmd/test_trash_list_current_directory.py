# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from datetime import datetime

from tests.support.my_path import MyPath
from tests.support.sort_lines import sort_lines

from tests.support.asserts import assert_equals_with_unidiff
from tests.test_list.cmd.support.trash_list_user import TrashListUser


class TestTrashListCurrentDirectory:
    def setup_method(self):
        self.user = TrashListUser(MyPath.make_temp_dir())

        self.user.set_fake_cwd("/home/user/currentdir")

    def test_currentdir_files_only(self):
        self.user.home().add_trashinfo4('/home/user/currentdir/file1',
                                        "2001-02-03 23:55:59")
        self.user.home().add_trashinfo4('/home/user/otherdir/file2',
                                        "2001-02-03 23:55:59")

        result = self.user.run_trash_list('--currentdir')

        assert_equals_with_unidiff(
            "2001-02-03 23:55:59 " + "/home/user/currentdir/file1\n",
            result.whole_output())

    def test_currentdir_nested_folders(self):
        self.user.home().add_trashinfo4('/home/user/otherdir/currentdir/file1',
                                        "2001-02-03 23:55:59")
        self.user.home().add_trashinfo4(
            '/home/user/currentdir/newdirectory/file2', "2001-02-03 23:55:59")

        result = self.user.run_trash_list('--currentdir')

        assert_equals_with_unidiff(
            "2001-02-03 23:55:59 " + "/home/user/currentdir/newdirectory/file2\n",
            result.whole_output())

    def test_should_output_currendir_should_not_show_currentdir_itself(self):
        self.user.home().add_trashinfo4("/home/user/currentdir",
                                        "2001-02-03 23:55:59")
        self.user.home().add_trashinfo4('/home/user/otherdir/file1',
                                        "2001-02-03 23:55:59")

        result = self.user.run_trash_list('--currentdir')

        assert_equals_with_unidiff("",
                                   result.whole_output())
