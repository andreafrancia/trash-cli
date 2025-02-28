# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import unittest

from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.put.describer import Describer


class TestDescriber(unittest.TestCase):
    def setUp(self):
        self.fs = FakeFs()
        self.describer = Describer(self.fs)

    def test_on_directories(self):
        self.fs.mkdir('a-dir')

        assert "directory" == self.describer.describe('.')
        assert "directory" == self.describer.describe("..")
        assert "directory" == self.describer.describe('a-dir')

    def test_on_dot_directories(self):
        self.fs.mkdir('a-dir')

        assert "'.' directory" == self.describer.describe("a-dir/.")
        assert "'.' directory" == self.describer.describe("./.")

    def test_on_dot_dot_directories(self):
        self.fs.mkdir('a-dir')

        assert "'..' directory" == self.describer.describe("./..")
        assert "'..' directory" == self.describer.describe("a-dir/..")

    def test_name_for_regular_files_non_empty_files(self):
        self.fs.make_file("non-empty", b"contents")

        assert "regular file" == self.describer.describe("non-empty")

    def test_name_for_empty_file(self):
        self.fs.make_file("empty")

        assert "regular empty file" == self.describer.describe("empty")

    def test_name_for_symbolic_links(self):
        self.fs.symlink("nowhere", "/symlink")

        assert "symbolic link" == self.describer.describe("symlink")

    def test_name_for_non_existent_entries(self):

        assert "non existent" == self.describer.describe('non-existent')
