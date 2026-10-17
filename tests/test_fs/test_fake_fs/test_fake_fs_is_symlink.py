import pytest

from tests.support.put.fake_fs.fake_fs import FakeFs


@pytest.fixture
def fake_fs():
    return FakeFs()

class TestFakeFsIsSymlink:

    def test_is_symlink_on_a_file(self, fake_fs):
        fake_fs.write_file("/foo", "content")

        assert fake_fs.is_symlink("/foo") is False

    def test_is_symlink_on_a_dir(self, fake_fs):
        fake_fs.mkdir("/foo")

        assert fake_fs.is_symlink("/foo") is False

    def test_is_symlink_on_a_link(self, fake_fs):
        fake_fs.symlink("dest", "/foo")

        assert fake_fs.is_symlink("/foo") is True

    def test_is_symlink_when_not_found(self, fake_fs):
        assert fake_fs.is_symlink("/foo") is False

    def test_is_symlink_when_directory_not_exisiting(self, fake_fs):
        assert fake_fs.is_symlink("/foo/bar/baz") is False
