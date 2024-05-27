import pytest

from tests.support.put.fake_fs.failing_fake_fs import FailingFakeFs
from tests.test_put.support.put_user import PutUser


class PutFixture:
    @pytest.fixture
    def user(self, fs):
        yield PutUser(fs)

    @pytest.fixture
    def fs(self):
        yield FailingFakeFs()
