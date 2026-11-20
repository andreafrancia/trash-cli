# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
from typing import Dict

import pytest

from tests.support.dates import jan_11_2001
from tests.support.dirs.my_path import MyPath
from tests.support.fake_fs.fake_volumes_listing import FakeVolumesListing
from six import StringIO

from tests.support.fakes.stub_volume_of import StubVolumeOfFs
from tests.support.fs_fixture import FsFixture, real_fs_fixture
from tests.support.dirs.temp_dir import temp_dir_fixture
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.empty.file_system_dir_reader import FileSystemDirReader
from trashcli.fslib.protocols.fs import Fs

fs = real_fs_fixture
temp_dir = temp_dir_fixture


@pytest.mark.slow
class TestEmptyCmdWithMultipleVolumesFs:
    @pytest.fixture(autouse=True)
    def setup_fs(self,
                 fs,  # type: Fs
                 temp_dir,   # type: MyPath
                 ):
        self.temp_dir = temp_dir
        self.top_dir = temp_dir / 'topdir'
        self.fsx = FsFixture(fs)
        self.fsx.require_empty_dir(self.top_dir)
        self.environ = dict()  # type: Dict[str, str]
        self.empty_cmd = EmptyCmd(
            argv0='trash-empty',
            out=StringIO(),
            err=StringIO(),
            volumes_listing=FakeVolumesListing([self.top_dir]),
            now=jan_11_2001,
            file_reader=fs,
            file_remover=ExistingFileRemover(fs),
            content_reader=fs,
            dir_reader=FileSystemDirReader(fs),
            version='unused',
            volumes=StubVolumeOfFs(),
        )

    def test_it_removes_trashinfos_from_method_1_dir(
            self, fs):  # type: (Fs) -> None
        self.fsx.make_proper_top_trash_dir(self.top_dir / '.Trash')
        self.fsx.make_empty_file(self.top_dir / '.Trash/123/info/foo.trashinfo')

        self.empty_cmd.run_cmd([], self.environ, uid=123)

        assert not fs.path_exists(
            self.top_dir / '.Trash/123/info/foo.trashinfo')

    def test_it_removes_trashinfos_from_method_2_dir(
            self, fs):  # type: (Fs) -> None
        self.fsx.make_empty_file(self.top_dir / '.Trash-123/info/foo.trashinfo')

        self.empty_cmd.run_cmd([], self.environ, uid=123)

        assert not fs.path_exists(
            self.top_dir / '.Trash-123/info/foo.trashinfo')

    def test_it_removes_trashinfo_from_specified_trash_dir(
            self, fs):  # type: (Fs) -> None
        self.fsx.make_empty_file(self.temp_dir / 'specified/info/foo.trashinfo')

        self.empty_cmd.run_cmd(['--trash-dir', self.temp_dir / 'specified'],
                               self.environ, uid=123)

        assert not fs.path_exists(
            self.temp_dir / 'specified/info/foo.trashinfo')
