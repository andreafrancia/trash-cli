import pytest

from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.fslib.real.real_fs import RealFs


@pytest.fixture
def real_fs_fixture():
    return RealFs()

@pytest.fixture
def fake_fs_fixture():
    return FakeFs()
