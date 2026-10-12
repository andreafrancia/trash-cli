from tests.support.capture_error import capture_error
from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.fslib.list_all import list_all


class TestMakeDirs:
    def setup_method(self):
        self.fs = FakeFs()

    def test_makedirs(self):
        self.fs.makedirs("/foo/bar/baz", 0o700)

        assert [
                   self.fs.path_isdir("/foo/bar/baz"),
                   self.fs.get_mod("/foo/bar/baz"),
               ] == [True, 0o700]

    def test_makedirs_2(self):
        self.fs.makedirs("/foo/bar/baz", 0o700)

        assert (sorted(list_all(self.fs, "/")) ==
                ['/foo', '/foo/bar', '/foo/bar/baz'])

    def test_makedirs_with_relative_paths(self):
        self.fs.makedirs("foo/bar/baz", 0o700)

        assert (sorted(list_all(self.fs, "/")) ==
                ['/foo', '/foo/bar', '/foo/bar/baz'])

    def test_makedirs_from_cur_dir_with_relative_paths(self):
        self.fs.mkdir("/cur_dir")
        self.fs.cd("/cur_dir")
        self.fs.makedirs("foo/bar/baz", 0o700)

        assert (sorted(list_all(self.fs, "/")) ==
                ['/cur_dir', '/cur_dir/foo', '/cur_dir/foo/bar',
                 '/cur_dir/foo/bar/baz'])

    def test_makedirs_from_cur_dir_with_absolute_path(self):
        self.fs.mkdir("/cur_dir")
        self.fs.cd("/cur_dir")
        self.fs.makedirs("/foo/bar/baz", 0o700)

        assert (sorted(list_all(self.fs, "/")) ==
                ['/cur_dir', '/foo', '/foo/bar', '/foo/bar/baz'])

    def test_makedirs_honor_file_permissions(self):
        self.fs.makedirs("/foo", 0o000)

        error = capture_error(
            lambda: self.fs.makedirs("/foo/bar", 0o755))

        assert str(error) == "[Errno 13] Permission denied: '/foo/bar'"

    def test_makedirs_with_exist_ok_bug__does_not_detect_a_file_in_place_of_a_dir(self):
        # Characterizes a known bug, not the desired behavior: unlike
        # os.makedirs (and RealFs.makedirs, which delegates to it),
        # exist_ok=True here suppresses EEXIST whenever the last path
        # component already exists, even when it is a file rather than
        # a directory. os.makedirs would still raise FileExistsError in
        # this case. This test should start failing, and be updated,
        # once FakeFs._makedirs is fixed to check that the existing
        # entry is a directory before suppressing the error.
        self.fs.write_file("/foo", "content")

        self.fs.makedirs("/foo", 0o700, exist_ok=True)

        assert self.fs.path_isdir("/foo") is False
