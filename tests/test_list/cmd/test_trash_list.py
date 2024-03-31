# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from datetime import datetime

from tests.support.sort_lines import sort_lines
from tests.test_list.cmd.setup import Setup

from tests.support.asserts import assert_equals_with_unidiff


class TestTrashList(Setup):

    def test_should_output_nothing_when_trashcan_is_empty(self):
        self.user.run_trash_list()

        assert_equals_with_unidiff('', self.user.output())

    def test_should_output_deletion_date_and_path(self):
        self.user.home_trashdir.add_trashinfo2('/absolute/path',
                                               datetime(2001, 2, 3, 23, 55, 59))

        self.user.run_trash_list()

        assert_equals_with_unidiff("2001-02-03 23:55:59 /absolute/path\n",
                                   self.user.output())

    def test_should_output_info_for_multiple_files(self):
        self.user.home_trashdir.add_trashinfo2("/file1",
                                               datetime(2000, 1, 1, 0, 0, 1))
        self.user.home_trashdir.add_trashinfo2("/file2",
                                               datetime(2000, 1, 1, 0, 0, 2))
        self.user.home_trashdir.add_trashinfo2("/file3",
                                               datetime(2000, 1, 1, 0, 0, 3))

        self.user.run_trash_list()
        output = self.user.output()

        assert_equals_with_unidiff("2000-01-01 00:00:01 /file1\n"
                                   "2000-01-01 00:00:02 /file2\n"
                                   "2000-01-01 00:00:03 /file3\n",
                                   sort_lines(output))

    def test_should_output_unknown_dates_with_question_marks(self):
        self.user.home_trashdir.add_trashinfo_without_date('without-date')

        self.user.run_trash_list()

        assert self.user.output() == "????-??-?? ??:??:?? /without-date\n"

    def test_should_output_invalid_dates_using_question_marks(self):
        self.user.home_trashdir.add_trashinfo_wrong_date('with-invalid-date',
                                                         'Wrong date')

        self.user.run_trash_list()

        assert_equals_with_unidiff("????-??-?? ??:??:?? /with-invalid-date\n",
                                   self.user.output())

    def test_should_warn_about_empty_trashinfos(self):
        self.user.home_trashdir.add_trashinfo_content('empty', '')

        self.user.run_trash_list()

        assert_equals_with_unidiff(
            "Parse Error: %(XDG_DATA_HOME)s/Trash/info/empty.trashinfo: "
            "Unable to parse Path.\n" % {"XDG_DATA_HOME": self.xdg_data_home},
            self.user.error())

    def test_should_warn_about_unreadable_trashinfo(self):
        self.user.home_trashdir.add_unreadable_trashinfo('unreadable')

        self.user.run_trash_list()

        assert_equals_with_unidiff(
            "[Errno 13] Permission denied: "
            "'%(XDG_DATA_HOME)s/Trash/info/unreadable.trashinfo'\n" % {
                'XDG_DATA_HOME': self.xdg_data_home
            },
            self.user.error())

    def test_should_warn_about_unexistent_path_entry(self):
        self.user.home_trashdir.add_trashinfo_without_path("foo")

        self.user.run_trash_list()

        assert_equals_with_unidiff(
            "Parse Error: %(XDG_DATA_HOME)s/Trash/info/foo.trashinfo: "
            "Unable to parse Path.\n" % {
                'XDG_DATA_HOME': self.xdg_data_home},
            self.user.error())
        assert_equals_with_unidiff('', self.user.output())
