# Copyright (C) 2011-2024 Andrea Francia Trivolzio(PV) Italy

import datetime

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

    def test_sort_by_date(self, user):
        user.home_trash_dir().add_trashinfo4('/file_b', "2000-01-01 00:00:03")
        user.home_trash_dir().add_trashinfo4('/file_a', "2000-01-01 00:00:01")
        user.home_trash_dir().add_trashinfo4('/file_c', "2000-01-01 00:00:02")

        output = user.run_trash_list('--sort=date')

        assert output.stdout == (
            "2000-01-01 00:00:01 /file_a\n"
            "2000-01-01 00:00:02 /file_c\n"
            "2000-01-01 00:00:03 /file_b\n")

    def test_sort_by_date_same_timestamp_sorts_by_path(self, user):
        user.home_trash_dir().add_trashinfo4('/file_c', "2000-01-01 00:00:01")
        user.home_trash_dir().add_trashinfo4('/file_a', "2000-01-01 00:00:01")
        user.home_trash_dir().add_trashinfo4('/file_b', "2000-01-01 00:00:01")

        output = user.run_trash_list('--sort=date')

        assert output.stdout == (
            "2000-01-01 00:00:01 /file_a\n"
            "2000-01-01 00:00:01 /file_b\n"
            "2000-01-01 00:00:01 /file_c\n")

    def test_sort_by_path(self, user):
        user.home_trash_dir().add_trashinfo4('/file_c', "2000-01-01 00:00:01")
        user.home_trash_dir().add_trashinfo4('/file_a', "2000-01-01 00:00:03")
        user.home_trash_dir().add_trashinfo4('/file_b', "2000-01-01 00:00:02")

        output = user.run_trash_list('--sort=path')

        assert output.stdout == (
            "2000-01-01 00:00:03 /file_a\n"
            "2000-01-01 00:00:02 /file_b\n"
            "2000-01-01 00:00:01 /file_c\n")

    def test_sort_by_path_same_path_sorts_by_date(self, user):
        user.home_trash_dir().add_trashinfo4('/same_file', "2000-01-01 00:00:03")
        user.home_trash_dir().add_trashinfo4('/same_file', "2000-01-01 00:00:01")
        user.home_trash_dir().add_trashinfo4('/same_file', "2000-01-01 00:00:02")

        output = user.run_trash_list('--sort=path')

        assert output.stdout == (
            "2000-01-01 00:00:01 /same_file\n"
            "2000-01-01 00:00:02 /same_file\n"
            "2000-01-01 00:00:03 /same_file\n")

    def test_sort_none_lists_all_entries(self, user):
        user.home_trash_dir().add_trashinfo4('/file_b', "2000-01-01 00:00:03")
        user.home_trash_dir().add_trashinfo4('/file_a', "2000-01-01 00:00:01")
        user.home_trash_dir().add_trashinfo4('/file_c', "2000-01-01 00:00:02")

        output = user.run_trash_list('--sort=none')

        assert output.all_lines() == {"2000-01-01 00:00:01 /file_a",
                                      "2000-01-01 00:00:02 /file_c",
                                      "2000-01-01 00:00:03 /file_b"}

    def test_sort_by_date_unknown_dates_sort_last(self, user):
        user.home_trash_dir().add_trashinfo4('/known', "2000-01-01 00:00:01")
        user.home_trash_dir().add_trashinfo_without_date('a-no-date')
        user.home_trash_dir().add_trashinfo_wrong_date('b-bad-date',
                                                       'Wrong date')

        output = user.run_trash_list('--sort=date')

        assert output.stdout == (
            "2000-01-01 00:00:01 /known\n"
            "????-??-?? ??:??:?? /a-no-date\n"
            "????-??-?? ??:??:?? /b-bad-date\n")

    def test_sort_by_path_with_unknown_dates(self, user):
        user.home_trash_dir().add_trashinfo_without_date('z-no-date')
        user.home_trash_dir().add_trashinfo4('/a-known', "2000-01-01 00:00:01")

        output = user.run_trash_list('--sort=path')

        assert output.stdout == (
            "2000-01-01 00:00:01 /a-known\n"
            "????-??-?? ??:??:?? /z-no-date\n")

    def test_sort_with_parse_errors_keeps_errors_on_stderr(self, user):
        user.home_trash_dir().add_trashinfo4('/file_b', "2000-01-01 00:00:02")
        user.home_trash_dir().add_trashinfo4('/file_a', "2000-01-01 00:00:01")
        user.home_trash_dir().add_trashinfo_content('broken', '')

        output = user.run_trash_list('--sort=date')

        assert output.stdout == (
            "2000-01-01 00:00:01 /file_a\n"
            "2000-01-01 00:00:02 /file_b\n")
        assert output.stderr == (
            "Parse Error: /xdg-data-home/Trash/info/broken.trashinfo: "
            "Unable to parse Path.\n")

    def test_sort_by_path_with_files_flag(self, user):
        user.home_trash_dir().add_trashinfo4('/file_b', "2000-01-01 00:00:01")
        user.home_trash_dir().add_trashinfo4('/file_a', "2000-01-01 00:00:01")

        output = user.run_trash_list('--sort=path', '--files')

        lines = output.stdout.splitlines()
        assert len(lines) == 2
        assert lines[0].startswith("2000-01-01 00:00:01 /file_a -> ")
        assert lines[1].startswith("2000-01-01 00:00:01 /file_b -> ")

    def test_sort_by_path_with_size_flag(self, user):
        user.home_trash_dir().add_trashed_file('big', '/file_a', 'X' * 10000)
        user.home_trash_dir().add_trashed_file('small', '/file_b', 'X')

        output = user.run_trash_list('--size', '--sort=path')

        assert output.stdout == (
            "10000 /file_a\n"
            "1 /file_b\n")

    def test_sort_by_date_with_size_flag(self, user):
        user.home_trash_dir().add_trashed_file(
            'a', '/file_a', 'X' * 100, datetime.datetime(2000, 1, 1, 0, 0, 2))
        user.home_trash_dir().add_trashed_file(
            'b', '/file_b', 'X', datetime.datetime(2000, 1, 1, 0, 0, 1))

        output = user.run_trash_list('--size', '--sort=date')

        assert output.stdout == (
            "1 /file_b\n"
            "100 /file_a\n")
