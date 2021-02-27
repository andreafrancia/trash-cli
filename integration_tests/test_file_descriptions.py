# Copyright (C) 2011-2021 Andrea Francia Bereguardo(PV) Italy

from trashcli.put import describe
from .files import require_empty_dir, make_empty_file, MyPath, make_file
import os
import unittest


class TestDescriptions(unittest.TestCase):
    def setUp(self):
        self.temp_dir = MyPath.make_temp_dir()
        require_empty_dir(self.temp_dir / 'sandbox')

    def test_on_directories(self):

        assert "directory" == describe('.')
        assert "directory" == describe("..")
        assert "directory" == describe(self.temp_dir / 'sandbox')

    def test_on_dot_directories(self):

        assert "'.' directory" ==  describe(self.temp_dir / "sandbox/.")
        assert "'.' directory" ==  describe("./.")

    def test_on_dot_dot_directories(self):

        assert "'..' directory" == describe("./..")
        assert "'..' directory" == describe(self.temp_dir / "sandbox/..")

    def test_name_for_regular_files_non_empty_files(self):

        make_file(self.temp_dir / "sandbox/non-empty", "contents")
        assert "regular file" == describe(self.temp_dir / "sandbox/non-empty")

    def test_name_for_empty_file(self):

        make_empty_file(self.temp_dir / 'sandbox/empty')
        assert "regular empty file" == describe(self.temp_dir / "sandbox/empty")

    def test_name_for_symbolic_links(self):

        os.symlink('nowhere', self.temp_dir / "sandbox/symlink")

        assert "symbolic link" == describe(self.temp_dir / "sandbox/symlink")

    def test_name_for_non_existent_entries(self):

        assert not os.path.exists(self.temp_dir / 'non-existent')

        assert "non existent" == describe(self.temp_dir / 'non-existent')
