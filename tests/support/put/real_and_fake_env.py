import os

import pytest

from tests.support.dirs.temp_dir import make_temp_dir
from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.fslib.fs_remove_file_if_exists import FsRemoveFileIfExists
from trashcli.fslib.real.real_entries_if_dir_exists import EntriesIfDirExistsImpl
from trashcli.fslib.real.real_fs import RealFs


class Env:
    """A directory (base) on a file system, to run the same test on the real
    file system (RealFs) and on the fake one (FakeFs)."""

    def __init__(self, fs, base, is_real, umask):
        self.fs = fs
        self.base = base
        self.is_real = is_real
        self._umask = umask
        # the real file system has these capabilities in separate classes
        self.dir_reader = EntriesIfDirExistsImpl(fs) if is_real else fs
        self.remover = FsRemoveFileIfExists(fs, {}, os.geteuid) if is_real else fs

    def path(self, name):
        return self.base + '/' + name

    def umask(self):
        return self._umask

    def make_sticky(self, path):
        if self.is_real:
            os.chmod(path, 0o1755)
        else:
            self.fs.set_sticky_bit(path)


@pytest.fixture
def env(request, process_umask):
    if request.param == 'real':
        fs = RealFs()
        tmp_dir = make_temp_dir(fs)
        yield Env(RealFs(), str(tmp_dir), True, process_umask)
        tmp_dir.clean_up()
    else:
        fs = FakeFs()
        fs.makedirs('/base', 0o755)
        yield Env(fs, '/base', False, 0)


def real_and_fake():
    return pytest.mark.parametrize(
        'env',
        [pytest.param('real', marks=pytest.mark.slow), 'fake'],
        indirect=True)
