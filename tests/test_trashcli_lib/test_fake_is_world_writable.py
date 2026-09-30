from tests.support.put.fake_fs.fake_fs import FakeFs
import pytest

@pytest.fixture
def fs():
    return FakeFs()


class TestFakeIsWorldWritable:
    def test_a_private_dir_is_not_world_writable(self, fs):
        fs.mkdir('/foo')
        fs.chmod ("/foo", 0o700)

        assert fs.is_world_writable('/foo') is False

    def test_a_world_writable_dir_is_detected(self, fs):
        fs.mkdir('/foo')
        fs.chmod("/foo", 0o777)

        assert fs.is_world_writable('/foo') is True

    def test_a_missing_path_is_not_world_writable(self, fs):
        assert fs.is_world_writable('/none') is False
