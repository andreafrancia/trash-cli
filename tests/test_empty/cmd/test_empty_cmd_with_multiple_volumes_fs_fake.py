# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import unittest

from tests.support.py2mock import Mock
from six import StringIO

from tests.support.fakes.stub_volume_of import StubVolumeOfFs
from tests.support.files import FsFixture
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.empty.file_system_dir_reader import FileSystemDirReader
from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.fslib.protocols.volumes_listing import VolumesListing


class TestEmptyCmdFakeWithMultipleVolumesFs(unittest.TestCase):
    def setUp(self):
        self.fs = FakeFs()
        self.temp_dir = '/tmp'
        self.top_dir = self.temp_dir + '/topdir'
        self.fsx = FsFixture(self.fs)
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

    def test_it_keeps_a_dir_renamed_to_the_trash_dir_name_after_the_listing(self):
        self.fsx.make_empty_file(self.top_dir + '/.Trash-123/info/foo.trashinfo')
        self.fsx.make_empty_file(self.top_dir + '/.Trash-123/files/foo')
        self.fsx.make_empty_file(self.top_dir + '/project/files/foo')
        lexists = self.fs.path_lexists

        def swap_then_check(path):
            if self.fs.path_exists(self.top_dir + '/project'):
                self.fs.move(self.top_dir + '/.Trash-123', self.top_dir + '/away')
                self.fs.move(self.top_dir + '/project', self.top_dir + '/.Trash-123')
            return lexists(path)

        self.fs.path_lexists = swap_then_check

        self.empty_cmd.run_cmd([], self.environ, uid=123)

        assert self.fs.path_exists(self.top_dir + '/.Trash-123/files/foo')

    def test_root_keeps_a_trash_dir_made_by_another_user(self):
        self.fsx.make_empty_file(self.top_dir + '/.Trash-0/info/foo.trashinfo')
        self.fs.geteuid = lambda: 0

        self.empty_cmd.run_cmd([], self.environ, uid=0)

        assert self.fs.path_exists(self.top_dir + '/.Trash-0/info/foo.trashinfo')
