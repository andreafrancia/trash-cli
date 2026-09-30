import os

from tests.support.put.real_and_fake_env import env, real_and_fake
from trashcli.put.fs.real_fs import RealFs
from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.restore.fs.protocols.restore_fs import RestoreFs

env = env  # the fixture, imported from its module

# both file systems can be used wherever a RestoreFs is expected
real_fs_as_restore_fs = RealFs()  # type: RestoreFs
fake_fs_as_restore_fs = FakeFs()  # type: RestoreFs


# The RestoreFs methods must answer the same on RealFs (real file system)
# and on FakeFs.
class TestRestoreFsLikeRealFs:
    @real_and_fake()
    def test_list_files_in_dir_returns_full_paths(self, env):
        env.fs.mkdirs(env.path('dir'))
        env.fs.make_file(env.path('dir/a'), 'a')
        env.fs.make_file(env.path('dir/b'), 'b')

        assert sorted(env.fs.list_files_in_dir(env.path('dir'))) == [
            env.path('dir/a'), env.path('dir/b')]

    @real_and_fake()
    def test_contents_of_returns_the_text(self, env):
        env.fs.make_file(env.path('file'), 'contents')

        assert env.fs.contents_of(env.path('file')) == 'contents'

    @real_and_fake()
    def test_path_exists_follows_symlinks_path_lexists_does_not(self, env):
        env.fs.make_file(env.path('file'), 'contents')
        env.fs.symlink('file', env.path('connected'))
        env.fs.symlink('missing', env.path('dangling'))

        assert [env.fs.path_exists(env.path(n)) for n in
                ['file', 'connected', 'dangling', 'none']] == [
                   True, True, False, False]
        assert [env.fs.path_lexists(env.path(n)) for n in
                ['file', 'connected', 'dangling', 'none']] == [
                   True, True, True, False]

    @real_and_fake()
    def test_path_isdir(self, env):
        env.fs.mkdirs(env.path('dir'))
        env.fs.make_file(env.path('file'), 'contents')
        env.fs.symlink('dir', env.path('to-dir'))
        env.fs.symlink('missing', env.path('dangling'))

        assert [env.fs.path_isdir(env.path(n)) for n in
                ['dir', 'file', 'to-dir', 'dangling', 'none']] == [
                   True, False, True, False, False]

    @real_and_fake()
    def test_mkdirs_creates_the_parents_and_accepts_existing_dirs(self, env):
        env.fs.mkdirs(env.path('a/b/c'))
        env.fs.mkdirs(env.path('a/b/c'))

        assert env.fs.path_isdir(env.path('a/b/c')) is True

    @real_and_fake()
    def test_move_and_remove_file(self, env):
        env.fs.make_file(env.path('file'), 'contents')

        env.fs.move(env.path('file'), env.path('moved'))

        assert env.fs.path_lexists(env.path('file')) is False
        assert env.fs.contents_of(env.path('moved')) == 'contents'
        env.fs.remove_file(env.path('moved'))
        assert env.fs.path_lexists(env.path('moved')) is False

    @real_and_fake()
    def test_getcwd_as_realpath(self, env):
        if not env.is_real:
            env.fs.cd('/some/dir')
            assert env.fs.getcwd_as_realpath() == '/some/dir'
        else:
            assert env.fs.getcwd_as_realpath() == os.path.realpath(os.curdir)

    @real_and_fake()
    def test_volume_of_is_a_mount_point_that_contains_the_path(self, env):
        volume = env.fs.volume_of(env.path('some/file'))

        assert env.path('some/file').startswith(volume)
        assert volume in list(env.fs.list_mount_points()) or volume == '/'
