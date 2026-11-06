# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import pytest

from tests.support.dirs.my_path import MyPath
from tests.support.empty.empty_user import EmptyUser
from tests.support.files import FsFixture
from tests.support.put.fake_fs.fake_fs import FakeFs


class TestEmptyWithVolumesFakeFs:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.fs = FakeFs()
        self.temp_dir = MyPath('/tmp', self.fs)
        self.top_dir = self.temp_dir / 'topdir'
        self.fsx = FsFixture(self.fs)
        self.fsx.require_empty_dir(self.top_dir)
        self.user = EmptyUser(self.fs)
        self.user.add_volume(self.top_dir)

    def test_it_removes_trashinfos_from_method_1_dir(self):
        trashinfo = self.top_dir / '.Trash/123/info/foo.trashinfo'
        self.fsx.make_proper_top_trash_dir(self.top_dir / '.Trash')
        self.fsx.make_empty_file(trashinfo)
        assert self.fs.path_exists(trashinfo)

        self.user.run_empty()

        assert not self.fs.path_exists(trashinfo)

    def test_it_removes_trashinfos_from_method_2_dir(self):
        trashinfo = self.top_dir / '.Trash-123/info/foo.trashinfo'
        self.fsx.make_empty_file(trashinfo)
        assert self.fs.path_exists(trashinfo)

        self.user.run_empty()

        assert not self.fs.path_exists(trashinfo)

    def test_it_removes_trashinfo_from_specified_trash_dir(self):
        trashinfo = self.temp_dir / 'specified/info/foo.trashinfo'
        self.fsx.make_empty_file(trashinfo)
        assert self.fs.path_exists(trashinfo)

        self.user.run_empty(['--trash-dir', self.temp_dir / 'specified'])

        assert not self.fs.path_exists(trashinfo)
