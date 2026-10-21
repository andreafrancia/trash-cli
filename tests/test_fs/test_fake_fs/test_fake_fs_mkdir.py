from tests.support.put.fake_fs.fake_fs import FakeFs


class TestFakeFsMkdir:
    def setup_method(self):
        self.fs = FakeFs('/')

    def test_mkdir__creates_a_dir(self):
        self.fs.mkdir("/foo")
        result = self.fs.ls_a("/")
        assert result == [".", "..", "foo"]

    def test_create_dir_in_dir(self):
        self.fs.mkdir("/foo")
        self.fs.mkdir("/foo/bar")
        result = self.fs.ls_a("/foo")
        assert result == [".", "..", "bar"]
