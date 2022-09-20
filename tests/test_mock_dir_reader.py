import unittest

from tests.mock_dir_reader import MockDirReader


class TestMockDirReader(unittest.TestCase):
    def setUp(self):
        self.fs = MockDirReader()

    def test_empty(self):
        result = self.fs.entries_if_dir_exists('/')
        self.assertEqual([], result)

    def test_add_file_in_root(self):
        self.fs.add_file('/foo')
        result = self.fs.entries_if_dir_exists('/')
        self.assertEqual(['foo'], result)

    def test_mkdir(self):
        self.fs.mkdir('/foo')
        result = self.fs.entries_if_dir_exists('/')
        self.assertEqual(['foo'], result)

    def test_add_file_in_dir(self):
        self.fs.mkdir('/foo')
        self.fs.add_file('/foo/bar')
        result = self.fs.entries_if_dir_exists('/')
        self.assertEqual(['foo'], result)
        result = self.fs.entries_if_dir_exists('/foo')
        self.assertEqual(['bar'], result)
