import os

import pytest

from tests.support.dirs.my_path import MyPath
from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.fslib.real.real_fs import RealFs


class Env:
    """A directory (base) on a file system, to run the same test on the real
    file system (RealFs) and on the fake one (FakeFs)."""

    def __init__(self, fs, base, is_real):
        self.fs = fs
        self.base = base
        self.is_real = is_real

    def path(self, name):
        return self.base + '/' + name

    def make_sticky(self, path):
        if self.is_real:
            os.chmod(path, 0o1755)
        else:
            self.fs.set_sticky_bit(path)


@pytest.fixture
def env(request):
    if request.param == 'real':
        tmp_dir = MyPath.make_temp_dir()
        yield Env(RealFs(), str(tmp_dir), True)
        tmp_dir.clean_up()
    else:
        fs = FakeFs()
        fs.makedirs('/base', 0o755)
        yield Env(fs, '/base', False)


def real_and_fake():
    return pytest.mark.parametrize('env', ['real', 'fake'], indirect=True)
