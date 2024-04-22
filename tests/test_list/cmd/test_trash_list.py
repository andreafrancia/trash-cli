# Copyright (C) 2011-2024 Andrea Francia Trivolzio(PV) Italy

from tests.support.run_command import temp_dir  # noqa
from tests.test_list.cmd.support.trash_list_user import trash_list_user

user = trash_list_user


class TestTrashList:
    def test_should_output_nothing_when_trashcan_is_empty(self, user):
        output = user.run_trash_list()

        assert output.whole_output() == ''

    def test_should_output_deletion_date_and_path(self, user):
        user.home_trash_dir().add_trashinfo4('/absolute/path',
                                             "2001-02-03 23:55:59")

        output = user.run_trash_list()

        assert (output.whole_output() == "2001-02-03 23:55:59 /absolute/path\n")

    def test_should_output_info_for_multiple_files(self, user):
        user.home_trash_dir().add_trashinfo4('/file1', "2000-01-01 00:00:01")
        user.home_trash_dir().add_trashinfo4('/file2', "2000-01-01 00:00:02")
        user.home_trash_dir().add_trashinfo4('/file3', "2000-01-01 00:00:03")

        output = user.run_trash_list()

        assert output.all_lines() == {"2000-01-01 00:00:01 /file1",
                                      "2000-01-01 00:00:02 /file2",
                                      "2000-01-01 00:00:03 /file3"}

    def test_should_output_unknown_dates_with_question_marks(self, user):
        user.home_trash_dir().add_trashinfo_without_date('without-date')

        output = user.run_trash_list()

        assert output.whole_output() == "????-??-?? ??:??:?? /without-date\n"

    def test_should_output_invalid_dates_using_question_marks(self, user):
        user.home_trash_dir().add_trashinfo_wrong_date('with-invalid-date',
                                                       'Wrong date')

        output = user.run_trash_list()

        assert (output.whole_output() ==
                "????-??-?? ??:??:?? /with-invalid-date\n")

    def test_should_warn_about_empty_trashinfos(self, user):
        user.home_trash_dir().add_trashinfo_content('empty', '')

        output = user.run_trash_list()

        assert output.err_and_out() == (
            "Parse Error: /xdg-data-home/Trash/info/empty.trashinfo: Unable "
            "to parse Path.\n", '')

    def test_should_warn_about_unreadable_trashinfo(self, user):
        user.home_trash_dir().add_unreadable_trashinfo('unreadable')

        output = user.run_trash_list()

        assert output.err_and_out() == (
            "[Errno 13] Permission denied: "
            "'/xdg-data-home/Trash/info/unreadable.trashinfo'\n",
            '')

    def test_should_warn_about_unexistent_path_entry(self, user):
        user.home_trash_dir().add_trashinfo_without_path("foo")

        output = user.run_trash_list()

        assert output.err_and_out() == (
            "Parse Error: /xdg-data-home/Trash/info/foo.trashinfo: "
            "Unable to parse Path.\n",
            '')
