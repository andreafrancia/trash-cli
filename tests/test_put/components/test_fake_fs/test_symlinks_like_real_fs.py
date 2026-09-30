from tests.support.put.real_and_fake_env import env, real_and_fake

env = env  # the fixture, imported from its module


# FakeFs must answer about symlinks exactly like RealFs (which works on the
# real file system): every test runs against both.
class TestSymlinksLikeRealFs:
    @real_and_fake()
    def test_islink_is_true_for_a_symlink(self, env):
        env.fs.symlink('target', env.path('link'))

        assert env.fs.islink(env.path('link')) is True

    @real_and_fake()
    def test_islink_is_false_for_files_dirs_and_missing_paths(self, env):
        env.fs.make_file(env.path('file'), 'contents')
        env.fs.makedirs(env.path('dir'), 0o755)

        assert env.fs.islink(env.path('file')) is False
        assert env.fs.islink(env.path('dir')) is False
        assert env.fs.islink(env.path('missing')) is False

    @real_and_fake()
    def test_lexists_is_true_for_a_dangling_symlink(self, env):
        env.fs.symlink('missing-target', env.path('link'))

        assert env.fs.lexists(env.path('link')) is True

    @real_and_fake()
    def test_exists_follows_the_symlink(self, env):
        env.fs.symlink('missing-target', env.path('dangling'))
        env.fs.make_file(env.path('file'), 'contents')
        env.fs.symlink('file', env.path('connected'))

        assert env.fs.path_exists(env.path('dangling')) is False
        assert env.fs.path_exists(env.path('connected')) is True

    @real_and_fake()
    def test_isdir_follows_the_symlink(self, env):
        env.fs.makedirs(env.path('dir'), 0o755)
        env.fs.symlink('dir', env.path('to-dir'))
        env.fs.symlink('missing-target', env.path('dangling'))

        assert env.fs.isdir(env.path('to-dir')) is True
        assert env.fs.isdir(env.path('dangling')) is False

    @real_and_fake()
    def test_isfile_follows_the_symlink(self, env):
        env.fs.make_file(env.path('file'), 'contents')
        env.fs.symlink('file', env.path('to-file'))
        env.fs.symlink('missing-target', env.path('dangling'))

        assert env.fs.isfile(env.path('to-file')) is True
        assert env.fs.isfile(env.path('dangling')) is False

    @real_and_fake()
    def test_readlink_returns_the_target_as_written(self, env):
        env.fs.symlink('relative/target', env.path('relative'))
        env.fs.symlink('/absolute/target', env.path('absolute'))

        assert env.fs.readlink(env.path('relative')) == 'relative/target'
        assert env.fs.readlink(env.path('absolute')) == '/absolute/target'

    @real_and_fake()
    def test_read_follows_a_relative_symlink(self, env):
        env.fs.makedirs(env.path('a/b'), 0o755)
        env.fs.make_file(env.path('a/b/file'), 'contents')
        env.fs.symlink('b/file', env.path('a/link'))

        assert env.fs.read(env.path('a/link')) == 'contents'

    @real_and_fake()
    def test_read_follows_an_absolute_symlink(self, env):
        env.fs.make_file(env.path('file'), 'contents')
        env.fs.symlink(env.path('file'), env.path('link'))

        assert env.fs.read(env.path('link')) == 'contents'

    @real_and_fake()
    def test_getsize_follows_the_symlink(self, env):
        env.fs.make_file(env.path('file'), 'contents')
        env.fs.symlink('file', env.path('link'))

        assert env.fs.getsize(env.path('link')) == len('contents')

    @real_and_fake()
    def test_remove_file_removes_the_link_and_not_the_target(self, env):
        env.fs.make_file(env.path('file'), 'contents')
        env.fs.symlink('file', env.path('link'))

        env.fs.remove_file(env.path('link'))

        assert env.fs.lexists(env.path('link')) is False
        assert env.fs.read(env.path('file')) == 'contents'

    @real_and_fake()
    def test_move_moves_the_link_itself(self, env):
        env.fs.make_file(env.path('file'), 'contents')
        env.fs.symlink('file', env.path('link'))

        env.fs.move(env.path('link'), env.path('moved'))

        assert env.fs.lexists(env.path('link')) is False
        assert env.fs.islink(env.path('moved')) is True
        assert env.fs.readlink(env.path('moved')) == 'file'

    @real_and_fake()
    def test_listdir_lists_symlinks(self, env):
        env.fs.make_file(env.path('file'), 'contents')
        env.fs.symlink('file', env.path('link'))

        assert sorted(env.fs.listdir(env.base)) == ['file', 'link']

    @real_and_fake()
    def test_walk_lists_a_symlink_to_a_dir_as_a_dir_but_does_not_follow_it(
            self, env):
        env.fs.makedirs(env.path('dir'), 0o755)
        env.fs.make_file(env.path('dir/inner'), 'contents')
        env.fs.symlink('dir', env.path('to-dir'))
        env.fs.symlink('missing-target', env.path('dangling'))
        env.fs.make_file(env.path('file'), 'contents')

        walked = [(top[len(env.base):], sorted(dirs), sorted(non_dirs))
                  for top, dirs, non_dirs in env.fs.walk_no_follow(env.base)]

        assert sorted(walked) == [
            ('', ['dir', 'to-dir'], ['dangling', 'file']),
            ('/dir', [], ['inner']),
        ]

    @real_and_fake()
    def test_has_sticky_bit_follows_the_symlink(self, env):
        env.fs.makedirs(env.path('sticky'), 0o755)
        env.fs.makedirs(env.path('plain'), 0o755)
        env.make_sticky(env.path('sticky'))
        env.fs.symlink('sticky', env.path('to-sticky'))
        env.fs.symlink('plain', env.path('to-plain'))

        assert env.fs.has_sticky_bit(env.path('to-sticky')) is True
        assert env.fs.has_sticky_bit(env.path('to-plain')) is False

    @real_and_fake()
    def test_a_sticky_dir_reached_through_a_symlink_is_a_sticky_dir(self, env):
        env.fs.makedirs(env.path('sticky'), 0o755)
        env.make_sticky(env.path('sticky'))
        env.fs.symlink('sticky', env.path('link'))

        assert env.fs.isdir(env.path('link')) is True
        assert env.fs.has_sticky_bit(env.path('link')) is True
