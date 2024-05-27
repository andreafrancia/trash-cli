# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import os
import unittest

from tests.support.py2mock import Mock
from six import StringIO

from tests.support.dirs.my_path import MyPath
from tests.support.fakes.stub_volume_of import StubVolumeOf
from tests.support.fs_fixture import FsFixture
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.empty.file_system_dir_reader import FileSystemDirReader
from trashcli.empty.main import FileSystemContentReader
from trashcli.empty.top_trash_dir_rules_file_system_reader import \
    RealTopTrashDirRulesReader
from trashcli.fstab.mount_points_listing import FakeMountPointsListing
from trashcli.put.fs.real_fs import RealFs


class TestEmptyCmdWithMultipleVolumesFs(unittest.TestCase):
    def setUp(self):
        self.fx = FsFixture(RealFs())
        self.temp_dir = MyPath.make_temp_dir()
        self.top_dir = self.temp_dir / 'topdir'
        self.fx.require_empty_dir(self.top_dir)
        self.environ = {}
        self.empty_cmd = EmptyCmd(
            argv0='trash-empty',
            out=StringIO(),
            err=StringIO(),
            now=None,
            file_reader=RealTopTrashDirRulesReader(),
            file_remover=ExistingFileRemover(),
            content_reader=FileSystemContentReader(),
            dir_reader=FileSystemDirReader(),
            version='unused',
            volumes=StubVolumeOf(),
            mount_point_listing=FakeMountPointsListing([self.top_dir])
        )
        self.fs = RealFs()

    def test_it_removes_trashinfos_from_method_1_dir(self):
        self.make_proper_top_trash_dir(self.top_dir / '.Trash')
        self.make_empty_file(self.top_dir / '.Trash/123/info/foo.trashinfo')

        self.empty_cmd.run_cmd([], self.environ, uid=123)

        assert not os.path.exists(
            self.top_dir / '.Trash/123/info/foo.trashinfo')

    def test_it_removes_trashinfos_from_method_2_dir(self):
        self.make_empty_file(self.top_dir / '.Trash-123/info/foo.trashinfo')

        self.empty_cmd.run_cmd([], self.environ, uid=123)

        assert not os.path.exists(
            self.top_dir / '.Trash-123/info/foo.trashinfo')

    def test_it_removes_trashinfo_from_specified_trash_dir(self):
        self.make_empty_file(self.temp_dir / 'specified/info/foo.trashinfo')

        self.empty_cmd.run_cmd(['--trash-dir', self.temp_dir / 'specified'],
                               self.environ, uid=123)

        assert not os.path.exists(
            self.temp_dir / 'specified/info/foo.trashinfo')

    def make_proper_top_trash_dir(self, path):
        self.fs.mkdir_p(path)
        self.fs.set_sticky_bit(path)

    def make_empty_file(self, path):
        FsFixture(self.fs).make_empty_file(path)

    def tearDown(self):
        self.temp_dir.clean_up()
