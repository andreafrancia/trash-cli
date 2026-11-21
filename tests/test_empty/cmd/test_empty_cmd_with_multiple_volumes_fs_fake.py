# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import unittest

from tests.support.dates import jan_11_2001
from tests.support.fake_fs.fake_volumes_listing import FakeVolumesListing
from six import StringIO

from tests.support.fakes.stub_volume_of import StubVolumeOfFs
from tests.support.fs_fixture import FsFixture
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.empty.file_system_dir_reader import FileSystemDirReader
from tests.support.put.fake_fs.fake_fs import FakeFs


class TestEmptyCmdFakeWithMultipleVolumesFs(unittest.TestCase):
    def setUp(self):
        self.fs = FakeFs()
        self.temp_dir = '/tmp'
        self.top_dir = self.temp_dir + '/topdir'
        self.fsx = FsFixture(self.fs)
        self.volumes_listing = FakeVolumesListing([self.top_dir])
        self.fsx.require_empty_dir(self.top_dir)
        self.environ = {}
        self.empty_cmd = EmptyCmd(
            argv0='trash-empty',
            out=StringIO(),
            err=StringIO(),
            volumes_listing=self.volumes_listing,
            now=jan_11_2001,
            file_reader=self.fs,
            file_remover=ExistingFileRemover(self.fs),
            content_reader=self.fs,
            dir_reader=FileSystemDirReader(self.fs),
            version='unused',
            volumes=StubVolumeOfFs(),
        )

    def test_it_removes_trashinfos_from_method_1_dir(self):
        self.fsx.make_proper_top_trash_dir(self.top_dir + '/.Trash')
        self.fsx.make_empty_file(self.top_dir + '/.Trash/123/info/foo.trashinfo')

        self.empty_cmd.run_cmd([], self.environ, uid=123)

        assert not self.fs.path_exists(
            self.top_dir + '/.Trash/123/info/foo.trashinfo')

    def test_it_removes_trashinfos_from_method_2_dir(self):
        self.fsx.make_empty_file(self.top_dir + '/.Trash-123/info/foo.trashinfo')

        self.empty_cmd.run_cmd([], self.environ, uid=123)

        assert not self.fs.path_exists(
            self.top_dir + '/.Trash-123/info/foo.trashinfo')

    def test_it_removes_trashinfo_from_specified_trash_dir(self):
        self.fsx.make_empty_file(self.temp_dir + '/specified/info/foo.trashinfo')

        self.empty_cmd.run_cmd(['--trash-dir', self.temp_dir + '/specified'],
                               self.environ, uid=123)

        assert not self.fs.path_exists(
            self.temp_dir + '/specified/info/foo.trashinfo')
