import pytest

from tests.support.files import FsFixture


@pytest.fixture
def unreadable_fixture(fs):
    class Unreadable:
        def __init__(self, fs):
            self.fs = fs
            self.unreadable_dirs = []

        def new_unreadable_dir(self, path):
            self.unreadable_dirs.append(path)
            FsFixture(fs).make_unreadable_dir(path)

        def make_readable(self):
            for path in self.unreadable_dirs:
                FsFixture(self.fs).make_readable(path)

    unreadable = Unreadable(fs)
    yield unreadable
    unreadable.make_readable()
