# Copyright (C) 2008-2021 Andrea Francia Bereguardo(PV) Italy
import pytest

from tests.support.dirs.my_path import MyPath
from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.support.fs_fixture import real_fs_fixture, FsFixture, fsx_fixture
from trashcli.fslib.protocols.fs import Fs

fs = real_fs_fixture
temp_dir = temp_dir_fixture
fsx = fsx_fixture


@pytest.mark.slow
class TestWithInSandbox:
    @pytest.fixture(autouse=True)
    def setup_fs(self,
                 fs,  # type: Fs
                 temp_dir,  # type: MyPath
                 fsx,  # type: FsFixture
                 ):
        self.temp_dir = temp_dir
        self.fs = fs
        self.fsx = fsx

    def test_mkdirs_with_default_mode(self):
        self.fs.makedirs(self.temp_dir / "test-dir/sub-dir")

        assert self.fs.path_isdir(self.temp_dir / "test-dir/sub-dir")

    def test_has_sticky_bit_returns_true(self):
        self.fsx.make_empty_file(self.temp_dir / "sticky")
        self.fsx.set_sticky_bit(self.temp_dir / "sticky")

        assert self.fs.has_sticky_bit(self.temp_dir / 'sticky')

    def test_has_sticky_bit_returns_false(self):
        self.fsx.make_empty_file(self.temp_dir / "non-sticky")
        self.fsx.set_sticky_bit(self.temp_dir / "non-sticky")
        self.fsx.unset_sticky_bit(self.temp_dir / "non-sticky")

        assert not self.fs.has_sticky_bit(self.temp_dir / "non-sticky")

class TestIsStickyDir:

    @pytest.fixture(autouse=True)
    def setup_fs(self,
                 fs,  # type: Fs
                 temp_dir,  # type: MyPath
                 fsx,  # type: FsFixture
                 ):
        self.temp_dir = temp_dir
        self.fs = fs
        self.fsx = fsx

    def test_dir_non_sticky(self):
        self.fs.makedirs(self.temp_dir / 'dir')

        assert not self.fs.is_sticky_dir(self.temp_dir / 'dir')

    def test_dir_sticky(self):
        self.fs.makedirs(self.temp_dir / 'dir')
        self.fsx.set_sticky_bit(self.temp_dir / 'dir')

        assert self.fs.is_sticky_dir(self.temp_dir / 'dir')

    def test_non_dir_but_sticky(self):
        self.fsx.make_empty_file(self.temp_dir / 'dir')
        self.fsx.set_sticky_bit(self.temp_dir / 'dir')

        assert not self.fs.is_sticky_dir(self.temp_dir / 'dir')

