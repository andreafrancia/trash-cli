import errno

import pytest

from tests.support.put.real_and_fake_env import env, real_and_fake

env = env  # the fixture, imported from its module


# Characterization of RealFs.read_file: FakeFs has to behave the same way.
class TestReadFileLikeRealFs:
    @real_and_fake()
    def test_reads_a_file(self, env):
        env.fs.write_file(env.path('file'), 'content')

        assert env.fs.read_file(env.path('file')) == 'content'

    @real_and_fake()
    def test_a_missing_file_raises_enoent(self, env):
        with pytest.raises(IOError) as e:
            env.fs.read_file(env.path('missing'))

        assert e.value.errno == errno.ENOENT
