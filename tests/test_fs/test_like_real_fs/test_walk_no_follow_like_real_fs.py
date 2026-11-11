from tests.support.put.real_and_fake_env import env, real_and_fake

env = env  # the fixture, imported from its module


def walk(env, path):
    return [(top[len(env.base):], sorted(dirs), sorted(files))
            for top, dirs, files in env.fs.walk_no_follow(path)]


# Characterization of RealFs.walk_no_follow (os.walk with followlinks=False):
# FakeFs has to behave the same way.
class TestWalkNoFollowLikeRealFs:
    @real_and_fake()
    def test_walks_dirs_and_files(self, env):
        env.fs.mkdirs(env.path('dir/subdir'))
        env.fs.write_file(env.path('dir/file'), 'a')

        assert walk(env, env.path('dir')) == [
            ('/dir', ['subdir'], ['file']),
            ('/dir/subdir', [], []),
        ]

    @real_and_fake()
    def test_skips_an_unreadable_subdir_silently(self, env):
        env.fs.mkdirs(env.path('dir/subdir'))
        env.fs.write_file(env.path('dir/subdir/file'), 'a')
        env.fs.chmod(env.path('dir/subdir'), 0o300)

        try:
            assert walk(env, env.path('dir')) == [
                ('/dir', ['subdir'], []),
            ]
        finally:
            env.fs.chmod(env.path('dir/subdir'), 0o700)
