import pytest

from tests.support.fakes.fake_trash_dir import FakeTrashDir
from tests.test_list.cmd.support.trash_list_user import trash_list_user  # noqa
from trashcli.lib.inconsistencies import inconsistencies_check_hint


# Without --doctor, trash-list prints one summary line per trash dir with
# inconsistencies, then a single hint about --doctor. The story reads top
# to bottom: a clean trash dir first, then a single malformed trashinfo,
# then several, then a non-trashinfo file, then several trash dirs.
class TestTrashListInconsistencies:
    @pytest.fixture
    def user(self, trash_list_user):
        u = trash_list_user
        u.set_fake_uid(123)
        return u

    HINT = "To check all inconsistencies run: `trash-list --doctor`"

    def test_no_summary_when_the_trash_dir_is_consistent(self, user):
        user.home_trash_dir().add_trashinfo4('/real-trash',
                                             "2001-02-03 23:55:59")

        output = user.run_trash_list()

        assert output.err_and_out() == (
            '', "2001-02-03 23:55:59 /real-trash\n")

    def test_summarizes_a_single_malformed_trashinfo(self, user):
        user.home_trash_dir().add_trashinfo_without_path('malformed')

        output = user.run_trash_list()

        assert output.err_and_out() == (
            "Found inconsistencies in /xdg-data-home/Trash\n" + self.HINT +
            "\n", '')

    def test_summarizes_many_malformed_trashinfo_in_one_line(self, user):
        user.home_trash_dir().add_trashinfo4('/real-trash',
                                             "2001-02-03 23:55:59")
        user.home_trash_dir().add_trashinfo_content('malformed', '')
        user.home_trash_dir().add_trashinfo_content('malformed2', '')
        user.home_trash_dir().add_trashinfo_without_path('malformed3')

        output = user.run_trash_list()

        assert output.err_and_out() == (
            "Found inconsistencies in /xdg-data-home/Trash\n" + self.HINT +
            "\n", "2001-02-03 23:55:59 /real-trash\n")

    def test_summarizes_a_non_trashinfo_file_in_the_info_dir(self, user):
        user.home_trash_dir().add_non_trashinfo('not-a-trashinfo')

        output = user.run_trash_list()

        assert output.err_and_out() == (
            "Found inconsistencies in /xdg-data-home/Trash\n" + self.HINT +
            "\n", '')

    def test_summarizes_once_for_each_trash_dir_with_problems(self, user):
        user.add_disk("disk")
        user.home_trash_dir().add_trashinfo_content('malformed', '')
        user.trash_dir2("disk").add_trashinfo_content('malformed', '')

        output = user.run_trash_list()

        assert output.err_and_out() == (
            "Found inconsistencies in /xdg-data-home/Trash\n"
            "Found inconsistencies in /disk/.Trash-123\n" + self.HINT +
            "\n", '')

    def test_hint_printed_once_when_many_trash_dirs_have_problems(self,
                                                                  user):
        user.add_disk("disk")
        user.home_trash_dir().add_trashinfo_content('malformed', '')
        user.trash_dir2("disk").add_trashinfo_content('malformed', '')

        output = user.run_trash_list()

        assert output.stderr.count(self.HINT) == 1

    def test_summary_shortens_the_home_dir(self, user):
        user.environ['HOME'] = user.root
        user.home_trash_dir().add_trashinfo_content('malformed', '')

        output = user.run_trash_list()

        assert output.stderr == (
            "Found inconsistencies in ~/xdg-data-home/Trash\n" + self.HINT +
            "\n")

    def test_hint_keeps_a_user_specified_trash_dir(self, user):
        custom_trash_dir = user.root / 'custom-trash'
        FakeTrashDir(custom_trash_dir).add_trashinfo_without_path('malformed')
        custom_path = str(custom_trash_dir).replace(str(user.root), '')

        output = user.run_trash_list('--trash-dir', str(custom_trash_dir))

        assert output.err_and_out() == (
            "Found inconsistencies in %s\n" % custom_path +
            "To check all inconsistencies run: `trash-list --doctor "
            "--trash-dir=%s`\n" % custom_path,
            '')

    def test_hint_keeps_the_all_users_scope(self):
        assert inconsistencies_check_hint(all_users=True) == (
            "To check all inconsistencies run: `trash-list --doctor "
            "--all-users`")
