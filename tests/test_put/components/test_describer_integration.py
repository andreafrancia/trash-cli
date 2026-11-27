# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import os
import unittest

import pytest

from tests.support.fs_fixture import FsFixture, real_fs_fixture, fsx_fixture
from tests.support.dirs.temp_dir import make_temp_dir, temp_dir_fixture
from trashcli.put.describer import Describer
from trashcli.fslib.real.real_fs import RealFs

fs = real_fs_fixture
temp_dir = temp_dir_fixture
fsx = fsx_fixture

@pytest.mark.slow
class TestDescriber:
    @pytest.fixture(autouse=True)
    def setup_sut(self, fs):
        self.describer = Describer(fs)

    def test_on_directories(self, fsx, temp_dir):
        fsx.require_empty_dir(temp_dir / 'a-dir')

        assert "directory" == self.describer.describe('.')
        assert "directory" == self.describer.describe("..")
        assert "directory" == self.describer.describe(temp_dir / 'a-dir')

    def test_on_dot_directories(self, fsx, temp_dir):
        fsx.require_empty_dir(temp_dir / 'a-dir')

        assert "'.' directory" == self.describer.describe(
            temp_dir / "a-dir/.")
        assert "'.' directory" == self.describer.describe("./.")

    def test_on_dot_dot_directories(self, fsx, temp_dir):
        fsx.require_empty_dir(temp_dir / 'a-dir')

        assert "'..' directory" == self.describer.describe("./..")
        assert "'..' directory" == self.describer.describe(temp_dir / "a-dir/..")

    def test_name_for_regular_files_non_empty_files(self, temp_dir, fsx):
        fsx.make_file(temp_dir / "non-empty", "contents")

        assert "regular file" == self.describer.describe(temp_dir / "non-empty")

    def test_name_for_empty_file(self, fsx, temp_dir):
        fsx.make_empty_file(temp_dir / 'empty')

        assert "regular empty file" == self.describer.describe(temp_dir / "empty")

    def test_name_for_symbolic_links(self, fs, temp_dir):
        fs.symlink('nowhere', temp_dir / "symlink")

        assert "symbolic link" == self.describer.describe(temp_dir / "symlink")

    def test_name_for_non_existent_entries(self, fs, temp_dir):
        assert not fs.path_exists(temp_dir / 'non-existent')

        assert "non existent" == self.describer.describe(temp_dir / 'non-existent')
