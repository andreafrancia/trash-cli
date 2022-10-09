import os
import unittest
from collections import OrderedDict


class File(object):
    def __init__(self, content):
        self.content = content


class Entry:
    def __init__(self,
                 file,  # type: File or Directory
                 mode,  # type: int
                 ):
        self.file = file
        self.mode = mode


class Directory():
    def __init__(self, name, parent_dir=None):
        self.name = name
        parent_dir = parent_dir or self
        self._entries = OrderedDict()
        self._entries['.'] = self
        self._entries['..'] = parent_dir

    def entries(self):
        return self._entries.keys()

    def add_dir(self, basename):
        self._entries[basename] = Entry(Directory(basename, self), 0o755)

    def get_file(self, basename):
        return self._entries[basename].file

    def add_file(self, basename, content):
        self._entries[basename] = Entry(File(content), 0o644)

    def get_entry(self, basename):  # type: (str) -> Entry
        return self._entries[basename]


class FakeFs():
    def __init__(self):
        self.root = Directory('/')

    def ls(self, path):
        dir = self.find_dir(path)
        return dir.entries()

    def mkdir(self, path):
        dirname, basename = os.path.split(path)
        dir = self.find_dir(dirname)
        dir.add_dir(basename)

    def find_dir(self, path):  # type: (str) -> Directory or File
        if path == '/':
            return self.root
        cur_dir = self.root
        components = path.split('/')
        for component in components[1:]:
            cur_dir = cur_dir.get_file(component)
        return cur_dir

    def atomic_write(self, path, content):
        self.make_file(path, content)

    def read(self, path):
        dirname, basenane = os.path.split(path)
        dir = self.find_dir(dirname)
        return dir.get_entry(basenane).file.content

    def make_file(self, path, content=''):
        dirname, basename = os.path.split(path)
        dir = self.find_dir(dirname)
        dir.add_file(basename, content)

    def get_mod(self, path):
        entry = self.find_entry(path)
        return entry.mode

    def find_entry(self, path):
        dirname, basename = os.path.split(path)
        dir = self.find_dir(dirname)
        return dir.get_entry(basename)

    def chmod(self, path, mode):
        entry = self.find_entry(path)
        entry.mode = mode


class TestFakeFs(unittest.TestCase):
    def setUp(self):
        self.fs = FakeFs()

    def test(self):
        result = self.fs.ls("/")
        assert result == [".", ".."]

    def test_create_dir(self):
        self.fs.mkdir("/foo")
        result = self.fs.ls("/")
        assert result == [".", "..", "foo"]

    def test_find_dir_root(self):
        assert '/' == self.fs.find_dir('/').name

    def test_find_dir_root_subdir(self):
        self.fs.mkdir("/foo")
        assert 'foo' == self.fs.find_dir('/foo').name

    def test_create_dir_in_dir(self):
        self.fs.mkdir("/foo")
        self.fs.mkdir("/foo/bar")
        result = self.fs.ls("/foo")
        assert result == [".", "..", "bar"]

    def test_create_file(self):
        self.fs.mkdir("/foo")
        self.fs.mkdir("/foo/bar")
        self.fs.atomic_write("/foo/bar/baz", "content")

        result = self.fs.read("/foo/bar/baz")

        assert result == "content"

    def test_chmod(self):
        self.fs.make_file("/foo")
        self.fs.chmod("/foo", 0o755)

        assert oct(self.fs.get_mod("/foo")) == oct(0o755)
