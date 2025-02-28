import unittest

from tests.support.put.fake_fs.fake_fs import FakeFs
from tests.support.put.format_mode import format_mode
from tests.support.capture_error import capture_error


class TestFakeFs(unittest.TestCase):
    def setUp(self):
        self.fs = FakeFs('/')

    def test(self):
        result = self.fs.ls_a("/")
        assert result == [".", ".."]

    def test_create_dir(self):
        self.fs.mkdir("/foo")
        result = self.fs.ls_a("/")
        assert result == [".", "..", "foo"]

    def test_find_dir_root(self):
        assert '/' == self.fs.get_entity_at('/').name

    def test_find_dir_root_subdir(self):
        self.fs.mkdir("/foo")
        assert 'foo' == self.fs.get_entity_at('/foo').name

    def test_create_dir_in_dir(self):
        self.fs.mkdir("/foo")
        self.fs.mkdir("/foo/bar")
        result = self.fs.ls_a("/foo")
        assert result == [".", "..", "bar"]

    def test_create_file(self):
        self.fs.mkdir("/foo")
        self.fs.mkdir("/foo/bar")
        self.fs.atomic_write("/foo/bar/baz", "content")

        result = self.fs.read_file("/foo/bar/baz")

        assert result == "content"

    def test_chmod(self):
        self.fs.make_file("/foo")
        self.fs.chmod("/foo", 0o755)

        assert oct(self.fs.get_mod("/foo")) == oct(0o755)

    def test_is_dir_when_file(self):
        self.fs.make_file("/foo")

        assert self.fs.isdir("/foo") is False

    def test_is_dir_when_dir(self):
        self.fs.mkdir("/foo")

        assert self.fs.isdir("/foo") is True

    def test_is_dir_when_it_does_not_exists(self):
        assert self.fs.isdir("/does-not-exists") is False

    def test_exists_false(self):
        assert self.fs.exists("/foo") is False

    def test_exists_true(self):
        self.fs.make_file("/foo")

        assert self.fs.exists("/foo") is True

    def test_remove_file(self):
        self.fs.make_file("/foo")
        self.fs.remove_file("/foo")

        assert self.fs.exists("/foo") is False

    def test_move(self):
        self.fs.make_file("/foo")
        self.fs.move("/foo", "/bar")

        assert self.fs.exists("/foo") is False
        assert self.fs.exists("/bar") is True

    def test_move_dir(self):
        self.fs.mkdir("/fruits")
        self.fs.make_file("/apple")
        self.fs.move("/apple", "/fruits")

        assert self.fs.ls_a('/fruits') == ['.', '..', 'apple']

    def test_islink_on_a_file(self):
        self.fs.make_file("/foo", b"content")

        assert self.fs.islink("/foo") is False

    def test_islink_on_a_link(self):
        self.fs.symlink("dest", "/foo")

        assert self.fs.islink("/foo") is True

    def test_set_sticky_bit_when_unset(self):
        self.fs.make_file("/foo")

        assert self.fs.has_sticky_bit("/foo") is False

    def test_set_sticky_bit_when_set(self):
        self.fs.make_file("/foo")
        self.fs.set_sticky_bit("/foo")

        assert self.fs.has_sticky_bit("/foo") is True

    def test_islink_when_not_found(self):
        assert self.fs.islink("/foo") is False

    def test_islink_when_directory_not_exisiting(self):
        assert self.fs.islink("/foo/bar/baz") is False

    def test_absolute_path(self):
        self.fs.make_file('/foo')
        assert b'' == self.fs.get_entity_at('/foo').content

    def test_relativae_path(self):
        self.fs.make_file('/foo', b'content')

        assert b'content' == self.fs.get_entity_at('foo').content

    def test_relativae_path_with_cd(self):
        self.fs.makedirs('/foo/bar', 0o755)
        self.fs.make_file('/foo/bar/baz', b'content')
        self.fs.cd('/foo/bar')

        assert b'content' == self.fs.get_entity_at('baz').content

    def test_isfile_with_file(self):
        self.fs.make_file('/foo')

        assert self.fs.isfile("/foo") is True

    def test_isfile_with_dir(self):
        self.fs.mkdir('/foo')

        assert self.fs.isfile("/foo") is False

    def test_getsize_with_empty_file(self):
        self.fs.make_file("foo")

        assert 0 == self.fs.get_file_size("foo")

    def test_get_file_size_with_non_empty_file(self):
        self.fs.make_file("foo", b"1234")

        assert 4 == self.fs.get_file_size("foo")

    def test_get_file_size_with_dir(self):
        self.fs.mkdir("foo")

        self.assertRaises(NotImplementedError, lambda: self.fs.get_file_size("foo"))

    def test_mode_lets_create_a_file(self):
        self.fs.makedirs("/foo/bar/baz", 0o755)

        self.fs.make_file("/foo/bar/baz/1", b"1")

        assert self.fs.isfile("/foo/bar/baz/1") is True

    def test_mode_does_not_let_create_a_file(self):
        self.fs.makedirs("/foo/bar/baz", 0o755)
        self.fs.chmod("/foo/bar/baz", 0o055)

        error = capture_error(
            lambda: self.fs.make_file("/foo/bar/baz/1", b"1"))

        assert str(error) == "[Errno 13] Permission denied: '/foo/bar/baz/1'"

    def test_get_mod_s_1(self):
        self.fs.make_file("/foo", b"content")

        assert format_mode(self.fs.get_mod("/foo")) == '0o644'

    def test_get_mod_s_2(self):
        self.fs.makedirs("/foo", 0o000)

        assert format_mode(self.fs.get_mod("/foo")) == '0o000'
