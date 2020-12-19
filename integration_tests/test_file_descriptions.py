# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from trashcli.put import describe
from .files import require_empty_dir, make_empty_file
import os
import unittest

class TestDescritions(unittest.TestCase):
    def setUp(self):
        require_empty_dir('sandbox')

    def test_on_directories(self):

        assert "directory" == describe('.')
        assert "directory" == describe("..")
        assert "directory" == describe("sandbox")

    def test_on_dot_directories(self):

        assert "'.' directory" ==  describe("sandbox/.")
        assert "'.' directory" ==  describe("./.")

    def test_on_dot_dot_directories(self):

        assert "'..' directory" == describe("./..")
        assert "'..' directory" == describe("sandbox/..")

    def test_name_for_regular_files_non_empty_files(self):

        write_file("sandbox/non-empty", "contents")
        assert "regular file" == describe("sandbox/non-empty")

    def test_name_for_empty_file(self):

        make_empty_file('sandbox/empty')
        assert "regular empty file" == describe("sandbox/empty")

    def test_name_for_symbolic_links(self):

        os.symlink('nowhere', "sandbox/symlink")

        assert "symbolic link" == describe("sandbox/symlink")

    def test_name_for_non_existent_entries(self):

        assert not os.path.exists('non-existent')

        assert "non existent" == describe('non-existent')

def write_file(path, contents):
    f = open(path, 'w')
    f.write(contents)
    f.close()

