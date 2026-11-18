import errno

import pytest

from tests.support.put.real_and_fake_env import env, real_and_fake
from trashcli.lib.trash_dir_remover import TrashDirRemover

env = env  # the fixture, imported from its module


@pytest.fixture
def remover(env):
    start_dir = env.fs.getcwd_as_realpath()
    env.fs.makedirs(env.path('Trash/files/dir/sub'))
    env.fs.write_file(env.path('Trash/files/dir/sub/file'), '')
    env.fs.write_file(env.path('Trash/files/x'), '')
    env.fs.makedirs(env.path('project/files'))
    env.fs.write_file(env.path('project/files/x'), '')
    yield TrashDirRemover(env.fs)
    env.fs.chdir(start_dir)


class TestTrashDirRemover:
    @real_and_fake()
    def test_a_file_and_a_dir_tree_are_removed(self, env, remover):
        start_dir = env.fs.getcwd_as_realpath()
        checked_dir = remover.check_trash_dir(env.path('Trash'), '/')

        remover.remove_if_exists(checked_dir, env.path('Trash/files/x'))
        remover.remove_if_exists(checked_dir, env.path('Trash/files/dir'))

        assert env.fs.listdir(env.path('Trash/files')) == []
        assert env.fs.getcwd_as_realpath() == start_dir

    @real_and_fake()
    def test_a_dir_renamed_to_the_trash_dir_name_after_the_listing_is_refused(self, env, remover):
        checked_dir = remover.check_trash_dir(env.path('Trash'), '/')
        env.fs.move(env.path('Trash'), env.path('away'))
        env.fs.move(env.path('project'), env.path('Trash'))

        with pytest.raises(OSError):
            remover.remove_if_exists(checked_dir, env.path('Trash/files/x'))

        assert env.fs.listdir(env.path('Trash/files')) == ['x']

    @real_and_fake()
    def test_a_files_dir_that_leads_elsewhere_is_refused(self, env, remover):
        checked_dir = remover.check_trash_dir(env.path('Trash'), '/')
        env.fs.shutil_rmtree(env.path('Trash/files'))
        env.fs.symlink(env.path('project/files'), env.path('Trash/files'))

        with pytest.raises(OSError):
            remover.remove_if_exists(checked_dir, env.path('Trash/files/x'))

        assert env.fs.listdir(env.path('project/files')) == ['x']

    @real_and_fake()
    def test_a_symlink_at_the_name_of_a_volume_trash_dir_is_refused(self, env, remover):
        env.fs.symlink(env.path('project'), env.path('.Trash-123'))

        with pytest.raises(OSError):
            remover.check_trash_dir(env.path('.Trash-123'), env.base)

    @real_and_fake()
    def test_a_symlink_to_the_home_trash_dir_is_followed(self, env, remover):
        env.fs.symlink(env.path('Trash'), env.path('link'))
        checked_dir = remover.check_trash_dir(env.path('link'), '/')

        remover.remove_if_exists(checked_dir, env.path('link/files/x'))

        assert env.fs.listdir(env.path('Trash/files')) == ['dir']

    @real_and_fake()
    def test_a_trash_dir_of_another_user_is_refused(self, env, remover, monkeypatch):
        uid = env.fs.geteuid()
        monkeypatch.setattr(env.fs, 'geteuid', lambda: uid + 1)

        with pytest.raises(OSError):
            remover.check_trash_dir(env.path('Trash'), '/')

    @real_and_fake()
    def test_a_start_dir_inside_the_removed_dir_is_no_error(self, env, remover):
        checked_dir = remover.check_trash_dir(env.path('Trash'), '/')
        env.fs.chdir(env.path('Trash/files/dir/sub'))

        remover.remove_if_exists(checked_dir, env.path('Trash/files/dir'))

        assert env.fs.listdir(env.path('Trash/files')) == ['x']

    @real_and_fake()
    def test_a_start_dir_that_is_gone_is_no_error(self, env, remover, monkeypatch):
        def no_start_dir():
            raise OSError(errno.ENOENT, 'No such file or directory')

        checked_dir = remover.check_trash_dir(env.path('Trash'), '/')
        monkeypatch.setattr(env.fs, 'getcwd_as_realpath', no_start_dir)

        remover.remove_if_exists(checked_dir, env.path('Trash/files/x'))

        assert env.fs.listdir(env.path('Trash/files')) == ['dir']
