# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from datetime import datetime

from tests.support.sort_lines import sort_lines
from tests.test_list.cmd.setup import Setup

from tests.support.asserts import assert_equals_with_unidiff


class TestTrashListCurrentDirectory(Setup):
    def setUp(self):
        super(type(self), self).setUp()
        self.user.set_fake_cwd("/home/user/currentdir")
                                   
    def test_currentdir_files_only(self):
        self.user.home_trashdir.add_trashinfo2('/home/user/currentdir/file1',
                                               datetime(2001, 2, 3, 23, 55, 59))
        self.user.home_trashdir.add_trashinfo2('/home/user/otherdir/file2',
                                               datetime(2001, 2, 3, 23, 55, 59))

        self.user.run_trash_list('--currentdir')

        assert_equals_with_unidiff("2001-02-03 23:55:59 " + "/home/user/currentdir/file1\n",
                                   self.user.output())

    def test_currentdir_nested_folders(self):
        self.user.home_trashdir.add_trashinfo2('/home/user/otherdir/currentdir/file1',
                                               datetime(2001, 2, 3, 23, 55, 59))
        self.user.home_trashdir.add_trashinfo2('/home/user/currentdir/newdirectory/file2',
                                               datetime(2001, 2, 3, 23, 55, 59))

        self.user.run_trash_list('--currentdir')

        assert_equals_with_unidiff("2001-02-03 23:55:59 " + "/home/user/currentdir/newdirectory/file2\n",
                                   self.user.output())


    def test_should_output_currendir_should_not_show_currentdir_itself(self):
        self.user.home_trashdir.add_trashinfo2("/home/user/currentdir",
                                               datetime(2001, 2, 3, 23, 55, 59))
        self.user.home_trashdir.add_trashinfo2('/home/user/otherdir/file1',
                                               datetime(2001, 2, 3, 23, 55, 59))

        self.user.run_trash_list('--currentdir')

        assert_equals_with_unidiff("",
                                   self.user.output())
