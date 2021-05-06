# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy
import unittest

from trashcli.trash import TrashDir


class TestTrashDir_finding_orphans(unittest.TestCase):
    def setUp(self):
        self.fs = FakeFileSystem()
        self.trash_dir = TrashDir(self.fs)

    def test(self):
        self.fs.create_fake_file('/info/foo.trashinfo')

        result = list(self.trash_dir.list_orphans('/'))

        assert [] == result

    def test2(self):
        self.fs.create_fake_file('/files/foo')

        result = list(self.trash_dir.list_orphans('/'))

        assert ['/files/foo'] == result


class FakeFileSystem:
    def __init__(self):
        self.files={}
        self.dirs={}
    def contents_of(self, path):
        return self.files[path]
    def exists(self, path):
        return path in self.files
    def entries_if_dir_exists(self, path):
        return self.dirs.get(path, [])
    def create_fake_file(self, path, contents=''):
        import os
        self.files[path] = contents
        self.create_fake_dir(os.path.dirname(path), os.path.basename(path))
    def create_fake_dir(self, dir_path, *dir_entries):
        self.dirs[dir_path] = dir_entries

class TestFakeFileSystem(unittest.TestCase):
    def setUp(self):
        self.fs = FakeFileSystem()
    def test_you_can_read_from_files(self):
        self.fs.create_fake_file('/path/to/file', "file contents")
        assert 'file contents' == self.fs.contents_of('/path/to/file')
    def test_when_creating_a_fake_file_it_creates_also_the_dir(self):
        self.fs.create_fake_file('/dir/file')
        assert set(('file',)) == set(self.fs.entries_if_dir_exists('/dir'))
    def test_you_can_create_multiple_fake_file(self):
        self.fs.create_fake_file('/path/to/file1', "one")
        self.fs.create_fake_file('/path/to/file2', "two")
        assert 'one' == self.fs.contents_of('/path/to/file1')
        assert 'two' == self.fs.contents_of('/path/to/file2')
    def test_no_file_exists_at_beginning(self):
        assert not self.fs.exists('/filename')
    def test_after_a_creation_the_file_exists(self):
        self.fs.create_fake_file('/filename')
        assert self.fs.exists('/filename')
    def test_create_fake_dir(self):
        self.fs.create_fake_dir('/etc', 'passwd', 'shadow', 'hosts')

        assert (set(['passwd', 'shadow', 'hosts']) ==
                     set(self.fs.entries_if_dir_exists('/etc')))
