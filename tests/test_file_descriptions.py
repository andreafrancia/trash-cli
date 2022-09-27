# Copyright (C) 2011-2021 Andrea Francia Bereguardo(PV) Italy
import pytest

from trashcli.put.trash_put_cmd import describe
from .files import require_empty_dir, make_empty_file, make_file
from .support import MyPath
import os
import unittest


@pytest.mark.slow
class TestDescriptions(unittest.TestCase):
    def setUp(self):
        self.temp_dir = MyPath.make_temp_dir()

    def test_on_directories(self):
        require_empty_dir(self.temp_dir / 'a-dir')

        assert "directory" == describe('.')
        assert "directory" == describe("..")
        assert "directory" == describe(self.temp_dir / 'a-dir')

    def test_on_dot_directories(self):
        require_empty_dir(self.temp_dir / 'a-dir')

        assert "'.' directory" ==  describe(self.temp_dir / "a-dir/.")
        assert "'.' directory" ==  describe("./.")

    def test_on_dot_dot_directories(self):
        require_empty_dir(self.temp_dir / 'a-dir')

        assert "'..' directory" == describe("./..")
        assert "'..' directory" == describe(self.temp_dir / "a-dir/..")

    def test_name_for_regular_files_non_empty_files(self):

        make_file(self.temp_dir / "non-empty", "contents")

        assert "regular file" == describe(self.temp_dir / "non-empty")

    def test_name_for_empty_file(self):

        make_empty_file(self.temp_dir / 'empty')

        assert "regular empty file" == describe(self.temp_dir / "empty")

    def test_name_for_symbolic_links(self):

        os.symlink('nowhere', self.temp_dir / "symlink")

        assert "symbolic link" == describe(self.temp_dir / "symlink")

    def test_name_for_non_existent_entries(self):

        assert not os.path.exists(self.temp_dir / 'non-existent')

        assert "non existent" == describe(self.temp_dir / 'non-existent')

    def tearDown(self):
        self.temp_dir.clean_up()
