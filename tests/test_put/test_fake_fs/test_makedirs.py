from tests.support.capture_error import capture_error
from tests.test_put.support.fake_fs.fake_fs import FakeFs


class TestMakeDirs:
    def setup_method(self):
        self.fs = FakeFs()

    def test_makedirs(self):
        self.fs.makedirs("/foo/bar/baz", 0o700)

        assert [
                   self.fs.isdir("/foo/bar/baz"),
                   self.fs.get_mod("/foo/bar/baz"),
               ] == [True, 0o700]

    def test_makedirs_honor_file_permissions(self):
        self.fs.makedirs("/foo", 0o000)

        error = capture_error(
            lambda: self.fs.makedirs("/foo/bar", 0o755))

        assert str(error) == "[Errno 13] Permission denied: '/foo/bar'"
