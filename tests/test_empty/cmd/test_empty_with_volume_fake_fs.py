# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import pytest

from tests.support.empty.empty_user import EmptyUser
from tests.support.files import FsFixture
from tests.support.dirs.temp_dir import temp_dir_fixture_fs
from tests.support.fs_fixture import fake_fs_fixture

fs = fake_fs_fixture
temp_dir = temp_dir_fixture_fs

class TestEmptyWithVolumesFakeFs:
    @pytest.fixture
    def top_dir(self, temp_dir, fsx):
        top_dir = temp_dir / 'topdir'
        fsx.require_empty_dir(top_dir)
        return top_dir

    @pytest.fixture
    def fsx(self, fs):
        return FsFixture(fs)

    @pytest.fixture
    def user(self, fs, top_dir):
        user = EmptyUser(fs)
        user.add_volume(top_dir)
        yield user

    def test_it_removes_trashinfos_from_method_1_dir(self,
                                                     fs,
                                                     user,
                                                     top_dir,
                                                     fsx,
                                                     ):
        trashinfo = top_dir / '.Trash/123/info/foo.trashinfo'
        fsx.make_proper_top_trash_dir(top_dir / '.Trash')
        fsx.make_empty_file(trashinfo)
        assert fs.path_exists(trashinfo)

        user.run_empty()

        assert not fs.path_exists(trashinfo)

    def test_it_removes_trashinfos_from_method_2_dir(self,
                                                     fs,
                                                     user,
                                                     top_dir,
                                                     fsx,
                                                     ):
        trashinfo = top_dir / '.Trash-123/info/foo.trashinfo'
        fsx.make_empty_file(trashinfo)
        assert fs.path_exists(trashinfo)

        user.run_empty()

        assert not fs.path_exists(trashinfo)

    def test_it_removes_trashinfo_from_specified_trash_dir(self,
                                                           fs,
                                                           user,
                                                           temp_dir,
                                                           fsx,
                                                           ):
        trashinfo = temp_dir / 'specified/info/foo.trashinfo'
        fsx.make_empty_file(trashinfo)
        assert fs.path_exists(trashinfo)

        user.run_empty(['--trash-dir', temp_dir / 'specified'])

        assert not fs.path_exists(trashinfo)
