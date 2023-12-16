from tests.test_put.support.fake_fs.fake_fs import FakeFs
from trashcli.put.fs.fs import list_all


class TestWalkNoFollow:
    def setup_method(self):
        self.fs = FakeFs()

    def test(self):
        self.fs.make_file("pippo")
        self.fs.makedirs("/a/b/c/d", 0o700)

        assert "\n".join(list_all(self.fs, "/")) == '/a\n' \
                                                    '/pippo\n' \
                                                    '/a/b\n' \
                                                    '/a/b/c\n' \
                                                    '/a/b/c/d'
