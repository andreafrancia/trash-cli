from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.compat import octal


class TestFakeFsMkdir:
    def setup_method(self):
        self.fs = FakeFs('/')

    def test_path_is_dir__will_detect_dir(self):
        self.fs.mkdir("/dir")

        assert self.fs.path_isdir("/dir")

    def test_path_is_dir__will_detect_file(self):
        self.fs.write_file("/file")

        assert not self.fs.path_isdir("/file")

    def test_path_is_dir__will_detect_link(self):
        self.fs.symlink("/file", "/link")

        assert not self.fs.path_isdir("/link")

    def test_mkdir__creates_a_dir(self):
        self.fs.mkdir("/foo")

        assert self.fs.path_isdir("/foo")

    def test_mkdir__create_dir_in_dir(self):
        self.fs.mkdir("/foo")

        self.fs.mkdir("/foo/bar")

        assert self.fs.path_isdir("/foo/bar")

    def test_mkdir__default_mode(self):
        self.fs.mkdir("/foo")

        assert octal(self.fs.get_mod("/foo")) == octal(0o755)

    def test_mkdir__with_mode(self):
        self.fs.mkdir("/foo", mode=0o111)

        assert octal(self.fs.get_mod("/foo")) == octal(0o111)
