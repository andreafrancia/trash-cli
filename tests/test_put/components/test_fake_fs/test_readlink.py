from tests.support.capture_error import capture_error
from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.put.fs.real_fs import RealFs
from tests.support.dirs.temp_dir import temp_dir

temp_dir = temp_dir


class TestReadLinkOnRealFs:
    def setup_method(self):
        self.fs = RealFs()

    def test_readlink(self, temp_dir):
        self.fs.symlink("target", temp_dir / "link")

        assert self.fs.readlink(temp_dir / "link") == "target"

    def test_readlink_on_regular_file(self, temp_dir):
        self.fs.make_file(temp_dir / "regular-file", b'contents')

        exc = capture_error(lambda: self.fs.readlink(temp_dir / "regular-file"))

        assert ((type(exc), str(exc).replace(temp_dir, '')) ==
                (OSError, "[Errno 22] Invalid argument: '/regular-file'"))

    def test_lexists(self, temp_dir):
        self.fs.symlink("target", temp_dir / "link")

        assert self.fs.lexists(temp_dir / "link") is True


class TestReadLink:
    def setup_method(self):
        self.fs = FakeFs()

    def test_readlink(self):
        self.fs.symlink("target", "link")

        assert self.fs.readlink("link") == "target"

    def test_readlink_for_non_links(self):
        self.fs.make_file("regular-file")

        exc = capture_error(lambda: self.fs.readlink("regular-file"))

        assert ((type(exc), str(exc)) ==
                (OSError, "[Errno 22] Invalid argument: '/regular-file'"))

    def test_read_file(self):
        self.fs.make_file("regular_file", b"contents")

        assert self.fs.read_file("regular_file") == b"contents"

    def test_read_linked_file(self):
        self.fs.make_file("regular_file", b"contents")
        self.fs.symlink("regular_file", "link")

        assert self.fs.read_file("link") == b"contents"

    def test_is_dir_for_links(self):
        self.fs.symlink("target", "link")

        assert self.fs.isdir("link") is False

    def test_read_linked_file_with_relative_path(self):
        self.fs.makedirs("/a/b/c/d", 0o777)
        self.fs.make_file("/a/b/c/d/regular_file", b"contents")

        self.fs.symlink("c/d/regular_file", "/a/b/link")

        assert self.fs.read_file("/a/b/link") == b"contents"

    def test_lexists(self):
        self.fs.symlink("target", "link")

        assert self.fs.lexists("link") is True
