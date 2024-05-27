# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import os
import unittest

import pytest

from tests.support.dirs.my_path import MyPath
from tests.support.fs_fixture import FsFixture
from trashcli.put.describer import Describer
from trashcli.put.fs.real_fs import RealFs


@pytest.mark.slow
class TestDescriber(unittest.TestCase):
    def setUp(self):
        fs = RealFs()
        self.temp_dir = MyPath.make_temp_dir()
        self.describer = Describer(fs)
        self.fx = FsFixture(fs)

    def test_on_directories(self):
        self.fx.require_empty_dir(self.temp_dir / 'a-dir')

        assert "directory" == self.describer.describe('.')
        assert "directory" == self.describer.describe("..")
        assert "directory" == self.describer.describe(self.temp_dir / 'a-dir')

    def test_on_dot_directories(self):
        self.fx.require_empty_dir(self.temp_dir / 'a-dir')

        assert "'.' directory" == self.describer.describe(
            self.temp_dir / "a-dir/.")
        assert "'.' directory" == self.describer.describe("./.")

    def test_on_dot_dot_directories(self):
        self.fx.require_empty_dir(self.temp_dir / 'a-dir')

        assert "'..' directory" == self.describer.describe("./..")
        assert "'..' directory" == self.describer.describe(self.temp_dir / "a-dir/..")

    def test_name_for_regular_files_non_empty_files(self):
        self.fx.make_file(self.temp_dir / "non-empty", b"contents")

        assert "regular file" == self.describer.describe(self.temp_dir / "non-empty")

    def test_name_for_empty_file(self):
        self.fx.make_empty_file(self.temp_dir / 'empty')

        assert "regular empty file" == self.describer.describe(self.temp_dir / "empty")

    def test_name_for_symbolic_links(self):
        os.symlink('nowhere', self.temp_dir / "symlink")

        assert "symbolic link" == self.describer.describe(self.temp_dir / "symlink")

    def test_name_for_non_existent_entries(self):
        assert not os.path.exists(self.temp_dir / 'non-existent')

        assert "non existent" == self.describer.describe(self.temp_dir / 'non-existent')

    def tearDown(self):
        self.temp_dir.clean_up()
