# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import os
import unittest

from tests.support.py2mock import Mock
from six import StringIO

from tests.support.fakes.stub_volume_of import StubVolumeOf
from tests.support.files import FsFixture
from tests.support.dirs.my_path import MyPath
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.empty.file_system_dir_reader import FileSystemDirReader
from trashcli.empty.main import FileSystemContentReader
from trashcli.fslib.real.real_fs import RealFs
from trashcli.fslib.protocols.volumes_listing import VolumesListing


class TestEmptyCmdWithMultipleVolumesFs(unittest.TestCase):
    def setUp(self):
        self.temp_dir = MyPath.make_temp_dir()
        self.top_dir = self.temp_dir / 'topdir'
        self.fsx = FsFixture(RealFs())
        self.volumes_listing = Mock(spec=VolumesListing)
        self.volumes_listing.list_volumes.return_value = [self.top_dir]
        self.fsx.require_empty_dir(self.top_dir)
        self.environ = {}
        self.empty_cmd = EmptyCmd(
            argv0='trash-empty',
            out=StringIO(),
            err=StringIO(),
            volumes_listing=self.volumes_listing,
            now=None,
            file_reader=RealFs(),
            file_remover=ExistingFileRemover(),
            content_reader=FileSystemContentReader(),
            dir_reader=FileSystemDirReader(),
            version='unused',
            volumes=StubVolumeOf(),
        )

    def test_it_removes_trashinfos_from_method_1_dir(self):
        self.fsx.make_proper_top_trash_dir(self.top_dir / '.Trash')
        self.fsx.make_empty_file(self.top_dir / '.Trash/123/info/foo.trashinfo')

        self.empty_cmd.run_cmd([], self.environ, uid=123)

        assert not os.path.exists(
            self.top_dir / '.Trash/123/info/foo.trashinfo')

    def test_it_removes_trashinfos_from_method_2_dir(self):
        self.fsx.make_empty_file(self.top_dir / '.Trash-123/info/foo.trashinfo')

        self.empty_cmd.run_cmd([], self.environ, uid=123)

        assert not os.path.exists(
            self.top_dir / '.Trash-123/info/foo.trashinfo')

    def test_it_removes_trashinfo_from_specified_trash_dir(self):
        self.fsx.make_empty_file(self.temp_dir / 'specified/info/foo.trashinfo')

        self.empty_cmd.run_cmd(['--trash-dir', self.temp_dir / 'specified'],
                               self.environ, uid=123)

        assert not os.path.exists(
            self.temp_dir / 'specified/info/foo.trashinfo')

    def tearDown(self):
        self.temp_dir.clean_up()
