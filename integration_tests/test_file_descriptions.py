# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from trashcli.trash import describe, write_file
from .files import require_empty_dir, having_file
from nose.tools import assert_equals
import os

class TestDescritions:
    def setUp(self):
        require_empty_dir('sandbox')

    def test_on_directories(self):

        assert_equals("directory", describe('.'))
        assert_equals("directory", describe(".."))
        assert_equals("directory", describe("sandbox"))

    def test_on_dot_directories(self):

        assert_equals("`.' directory",  describe("sandbox/."))
        assert_equals("`.' directory",  describe("./."))

    def test_on_dot_dot_directories(self):

        assert_equals("`..' directory", describe("./.."))
        assert_equals("`..' directory", describe("sandbox/.."))

    def test_name_for_regular_files_non_empty_files(self):

        write_file("sandbox/non-empty", "contents")
        assert_equals("regular file", describe("sandbox/non-empty"))

    def test_name_for_empty_file(self):

        having_file('sandbox/empty')
        assert_equals("regular empty file", describe("sandbox/empty"))

    def test_name_for_symbolic_links(self):

        os.symlink('nowhere', "sandbox/symlink")

        assert_equals("symbolic link", describe("sandbox/symlink"))

    def test_name_for_non_existent_entries(self):

        assert not os.path.exists('non-existent')

        assert_equals("non existent", describe('non-existent'))
