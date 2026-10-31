import pytest

from tests.test_list.cmd.support.trash_list_user import trash_list_user  # noqa


# Malformed trashinfo files and non .trashinfo files in the info dir are
# summarized by trash-list in one line per trash dir, while
# trash-list --doctor reports them one by one.
class TestTrashListDoctor:
    @pytest.fixture
    def user(self, trash_list_user):
        u = trash_list_user
        u.set_fake_uid(123)
        return u

    def test_summarizes_many_malformed_trashinfo_in_one_line(self, user):
        user.home_trash_dir().add_trashinfo4('/real-trash',
                                             "2001-02-03 23:55:59")
        user.home_trash_dir().add_trashinfo_content('malformed', '')
        user.home_trash_dir().add_trashinfo_content('malformed2', '')
        user.home_trash_dir().add_trashinfo_without_path('malformed3')

        output = user.run_trash_list()

        assert output.err_and_out() == (
            "Found inconsistencies in /xdg-data-home/Trash check them "
            "running `trash-list --doctor`\n",
            "2001-02-03 23:55:59 /real-trash\n")

    def test_summarizes_a_non_trashinfo_file_in_the_info_dir(self, user):
        user.home_trash_dir().add_non_trashinfo('not-a-trashinfo')

        output = user.run_trash_list()

        assert output.err_and_out() == (
            "Found inconsistencies in /xdg-data-home/Trash check them "
            "running `trash-list --doctor`\n", '')

    def test_summarizes_once_for_each_trash_dir_with_problems(self, user):
        user.add_disk("disk")
        user.home_trash_dir().add_trashinfo_content('malformed', '')
        user.trash_dir2("disk").add_trashinfo_content('malformed', '')

        output = user.run_trash_list()

        assert output.err_and_out() == (
            "Found inconsistencies in /xdg-data-home/Trash check them "
            "running `trash-list --doctor`\n"
            "Found inconsistencies in /disk/.Trash-123 check them "
            "running `trash-list --doctor`\n", '')

    def test_summary_shortens_the_home_dir(self, user):
        user.environ['HOME'] = user.root
        user.home_trash_dir().add_trashinfo_content('malformed', '')

        output = user.run_trash_list()

        assert output.stderr == (
            "Found inconsistencies in ~/xdg-data-home/Trash check them "
            "running `trash-list --doctor`\n")

    def test_no_summary_when_the_trash_dir_is_consistent(self, user):
        user.home_trash_dir().add_trashinfo4('/real-trash',
                                             "2001-02-03 23:55:59")

        output = user.run_trash_list()

        assert output.err_and_out() == (
            '', "2001-02-03 23:55:59 /real-trash\n")

    def test_doctor_reports_each_malformed_trashinfo(self, user):
        user.home_trash_dir().add_trashinfo4('/real-trash',
                                             "2001-02-03 23:55:59")
        user.home_trash_dir().add_trashinfo_content('malformed', '')
        user.home_trash_dir().add_trashinfo_without_path('malformed2')

        output = user.run_trash_list('--doctor')

        assert (output.stderr, sorted(output.stdout.splitlines())) == ('', [
            "Parse Error: /xdg-data-home/Trash/info/malformed.trashinfo: "
            "Unable to parse Path.",
            "Parse Error: /xdg-data-home/Trash/info/malformed2.trashinfo: "
            "Unable to parse Path.",
        ])

    def test_doctor_reports_a_non_trashinfo_file_in_the_info_dir(self, user):
        user.home_trash_dir().add_non_trashinfo('not-a-trashinfo')

        output = user.run_trash_list('--doctor')

        assert output.err_and_out() == (
            '',
            "Non .trashinfo file in info dir: "
            "/xdg-data-home/Trash/info/not-a-trashinfo\n")

    def test_doctor_prints_nothing_when_the_trash_dir_is_consistent(self,
                                                                    user):
        user.home_trash_dir().add_trashinfo4('/real-trash',
                                             "2001-02-03 23:55:59")

        output = user.run_trash_list('--doctor')

        assert output.err_and_out() == ('', '')
