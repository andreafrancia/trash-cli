# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from trashcli.put import describe
from .files import require_empty_dir, having_file
from nose.tools import assert_equal
import os

class TestDescritions:
    def setUp(self):
        require_empty_dir('sandbox')

    def test_on_directories(self):

        assert_equal("directory", describe('.'))
        assert_equal("directory", describe(".."))
        assert_equal("directory", describe("sandbox"))

    def test_on_dot_directories(self):

        assert_equal("'.' directory",  describe("sandbox/."))
        assert_equal("'.' directory",  describe("./."))

    def test_on_dot_dot_directories(self):

        assert_equal("'..' directory", describe("./.."))
        assert_equal("'..' directory", describe("sandbox/.."))

    def test_name_for_regular_files_non_empty_files(self):

        write_file("sandbox/non-empty", "contents")
        assert_equal("regular file", describe("sandbox/non-empty"))

    def test_name_for_empty_file(self):

        having_file('sandbox/empty')
        assert_equal("regular empty file", describe("sandbox/empty"))

    def test_name_for_symbolic_links(self):

        os.symlink('nowhere', "sandbox/symlink")

        assert_equal("symbolic link", describe("sandbox/symlink"))

    def test_name_for_non_existent_entries(self):

        assert not os.path.exists('non-existent')

        assert_equal("non existent", describe('non-existent'))

def write_file(path, contents):
    f = open(path, 'w')
    f.write(contents)
    f.close()

