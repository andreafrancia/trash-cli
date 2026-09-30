import pytest

from tests.support.dirs.my_path import MyPath
from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.put.fs.real_fs import RealFs


class Env:
    def __init__(self, fs, base):
        self.fs = fs
        self.base = base

    def path(self, name):
        return self.base + '/' + name


@pytest.fixture
def env(request):
    if request.param == 'real':
        tmp_dir = MyPath.make_temp_dir()
        yield Env(RealFs(), str(tmp_dir))
        tmp_dir.clean_up()
    else:
        fs = FakeFs()
        fs.makedirs('/base', 0o755)
        yield Env(fs, '/base')


def real_and_fake():
    return pytest.mark.parametrize('env', ['real', 'fake'], indirect=True)


def real_and_fake_but_fake_diverges(reason):
    return pytest.mark.parametrize(
        'env',
        ['real', pytest.param('fake', marks=pytest.mark.xfail(strict=True,
                                                               reason=reason))],
        indirect=True)


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

    @real_and_fake_but_fake_diverges(
        'FakeFs.exists crashes on symlinks')
    def test_exists_follows_the_symlink(self, env):
        env.fs.symlink('missing-target', env.path('dangling'))
        env.fs.make_file(env.path('file'), 'contents')
        env.fs.symlink('file', env.path('connected'))

        assert env.fs.exists(env.path('dangling')) is False
        assert env.fs.exists(env.path('connected')) is True

    @real_and_fake_but_fake_diverges(
        'FakeFs.isdir is False for a symlink to a dir')
    def test_isdir_follows_the_symlink(self, env):
        env.fs.makedirs(env.path('dir'), 0o755)
        env.fs.symlink('dir', env.path('to-dir'))
        env.fs.symlink('missing-target', env.path('dangling'))

        assert env.fs.isdir(env.path('to-dir')) is True
        assert env.fs.isdir(env.path('dangling')) is False

    @real_and_fake_but_fake_diverges(
        'FakeFs.isfile crashes on symlinks')
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

    @real_and_fake_but_fake_diverges(
        'FakeFs.getsize crashes on symlinks')
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

    @real_and_fake_but_fake_diverges(
        'FakeFs.walk_no_follow lists a symlink to a dir as a non dir')
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
