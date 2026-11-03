import pytest

from tests.test_list.cmd.support.trash_list_user import trash_list_user  # noqa


# trash-list --doctor reports each inconsistency one by one, without
# summarizing. The story reads top to bottom: a clean trash dir first,
# then a single malformed trashinfo, then several, then a non-trashinfo
# file in the info dir.
class TestTrashListDoctor:
    @pytest.fixture
    def user(self, trash_list_user):
        u = trash_list_user
        u.set_fake_uid(123)
        return u

    def test_doctor_prints_nothing_when_the_trash_dir_is_consistent(self,
                                                                    user):
        user.home_trash_dir().add_trashinfo4('/real-trash',
                                             "2001-02-03 23:55:59")

        output = user.run_trash_list('--doctor')

        assert output.err_and_out() == ('', '')

    def test_doctor_reports_a_single_malformed_trashinfo(self, user):
        user.home_trash_dir().add_trashinfo_without_path('malformed')

        output = user.run_trash_list('--doctor')

        assert output.stderr == ''
        assert output.stdout == (
            "Parse Error: /xdg-data-home/Trash/info/malformed.trashinfo: "
            "Unable to parse Path.\n")

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
