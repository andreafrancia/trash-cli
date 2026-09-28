import pytest

from tests.support.put.fake_fs.fake_fs import FakeFs


@pytest.fixture
def fake_fs():
    return FakeFs()

class TestFakeFsIsStickyDir:

    def test_is_sticky_dir_when_dir_without_sticky_bit(self, fake_fs):
        fake_fs.mkdir("/foo")

        assert fake_fs.is_sticky_dir("/foo") is False

    def test_is_sticky_dir_when_dir_with_sticky_bit(self, fake_fs):
        fake_fs.mkdir("/foo")
        fake_fs.set_sticky_bit("/foo")

        assert fake_fs.is_sticky_dir("/foo") is True

    def test_is_sticky_dir_when_file_with_sticky_bit(self, fake_fs):
        fake_fs.make_file("/foo")
        fake_fs.set_sticky_bit("/foo")

        assert fake_fs.is_sticky_dir("/foo") is False

    def test_is_sticky_dir_when_file_without_sticky_bit(self, fake_fs):
        fake_fs.make_file("/foo")

        assert fake_fs.is_sticky_dir("/foo") is False

    def test_is_sticky_dir_when_path_does_not_exist(self, fake_fs):
        assert fake_fs.is_sticky_dir("/does-not-exist") is False

