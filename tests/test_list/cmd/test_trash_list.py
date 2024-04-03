# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from datetime import datetime

from tests.support.sort_lines import sort_lines
from tests.test_list.cmd.setup import Setup

from tests.support.asserts import assert_equals_with_unidiff


class TestTrashList(Setup):

    def test_should_output_nothing_when_trashcan_is_empty(self):
        output = self.user.run_trash_list()

        assert_equals_with_unidiff('', output.whole_output())

    def test_should_output_deletion_date_and_path(self):
        self.user.add_home_trashinfo('/absolute/path', "2001-02-03 23:55:59")

        output = self.user.run_trash_list()

        assert_equals_with_unidiff("2001-02-03 23:55:59 /absolute/path\n",
                                   output.whole_output())

    def test_should_output_info_for_multiple_files(self):
        self.user.add_home_trashinfo('/file1', "2000-01-01 00:00:01")
        self.user.add_home_trashinfo('/file2', "2000-01-01 00:00:02")
        self.user.add_home_trashinfo('/file3', "2000-01-01 00:00:03")

        output = self.user.run_trash_list()

        assert_equals_with_unidiff("2000-01-01 00:00:01 /file1\n"
                                   "2000-01-01 00:00:02 /file2\n"
                                   "2000-01-01 00:00:03 /file3\n",
                                   sort_lines(output.whole_output()))

    def test_should_output_unknown_dates_with_question_marks(self):
        self.user.add_home_trashinfo_without_date('without-date')

        output = self.user.run_trash_list()

        assert output.whole_output() == "????-??-?? ??:??:?? /without-date\n"

    def test_should_output_invalid_dates_using_question_marks(self):
        self.user.add_trashinfo_wrong_date('with-invalid-date', 'Wrong date')

        output = self.user.run_trash_list()

        assert_equals_with_unidiff("????-??-?? ??:??:?? /with-invalid-date\n",
                                   output.whole_output())

    def test_should_warn_about_empty_trashinfos(self):
        self.user.add_home_trash_with_content('empty', '')

        output = self.user.run_trash_list()

        assert_equals_with_unidiff(
            "Parse Error: %(XDG_DATA_HOME)s/Trash/info/empty.trashinfo: "
            "Unable to parse Path.\n" % {"XDG_DATA_HOME": self.xdg_data_home},
            output.whole_output())

    def test_should_warn_about_unreadable_trashinfo(self):
        self.user.add_unreadable_trashinfo('unreadable')

        output = self.user.run_trash_list()

        assert_equals_with_unidiff(
            "[Errno 13] Permission denied: "
            "'%(XDG_DATA_HOME)s/Trash/info/unreadable.trashinfo'\n" % {
                'XDG_DATA_HOME': self.xdg_data_home
            }, output.stderr)

    def test_should_warn_about_unexistent_path_entry(self):
        self.user.add_trashinfo_without_path("foo")

        output = self.user.run_trash_list()

        assert_equals_with_unidiff(
            "Parse Error: %(XDG_DATA_HOME)s/Trash/info/foo.trashinfo: "
            "Unable to parse Path.\n" % {
                'XDG_DATA_HOME': self.xdg_data_home},
            output.stderr)
        assert_equals_with_unidiff('', output.stdout)
