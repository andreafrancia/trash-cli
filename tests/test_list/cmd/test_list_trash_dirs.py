import pytest

from tests.test_list.cmd.support.trash_list_user import trash_list_user  # noqa


class TestListTrashDirs:
    @pytest.fixture
    def user(self, trash_list_user):
        u = trash_list_user
        u.set_fake_uid(123)
        return u

    def test_lists_the_home_trash_dir(self, user):
        output = user.run_trash_list('--trash-dirs')

        assert output.err_and_out() == ('', '/xdg-data-home/Trash\n')

    def test_lists_the_trash_dirs_of_a_volume(self, user):
        user.add_disk("disk")
        user.trash_dir1("disk").make_parent_sticky()
        user.trash_dir1("disk").make_dir()
        user.fsx.make_empty_dir(user.trash_dir2("disk").path)

        output = user.run_trash_list('--trash-dirs')

        assert output.err_and_out() == ('', '/xdg-data-home/Trash\n'
                                            '/disk/.Trash/123\n'
                                            '/disk/.Trash-123\n')

    def test_does_not_list_the_trash_dirs_that_does_not_exist(self, user):
        user.add_disk("disk")
        user.trash_dir1("disk").make_parent_sticky()

        output = user.run_trash_list('--trash-dirs')

        assert output.err_and_out() == ('', '/xdg-data-home/Trash\n')

    def test_reports_when_the_parent_is_not_sticky(self, user):
        user.add_disk("disk")
        user.trash_dir1("disk").make_parent_unsticky()
        user.trash_dir1("disk").make_dir()

        output = user.run_trash_list('--trash-dirs')

        assert output.err_and_out() == ('', '/xdg-data-home/Trash\n'
                                            'parent_not_sticky: /disk/.Trash/123\n')

    def test_reports_when_the_parent_is_a_symlink_to_a_sticky_dir(self, user):
        user.add_disk("disk")
        user.trash_dir1("disk").make_parent_symlink()
        user.fsx.set_sticky_bit(user.root / "disk" / ".Trash-dest")
        user.trash_dir1("disk").make_dir()

        output = user.run_trash_list('--trash-dirs')

        assert output.err_and_out() == ('', '/xdg-data-home/Trash\n'
                                            'parent_is_symlink: /disk/.Trash/123\n')

    def test_lists_only_the_trash_dirs_specified_by_the_user(self, user):
        user.add_disk("disk")

        output = user.run_trash_list('--trash-dirs',
                                     '--trash-dir=/specified/Trash1',
                                     '--trash-dir=/specified/Trash2')

        assert output.err_and_out() == ('', '/specified/Trash1\n'
                                            '/specified/Trash2\n')
