# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import os
import unittest

from mock import Mock
from six import StringIO

from tests.files import require_empty_dir, make_dirs, set_sticky_bit, \
    make_empty_file
from tests.support import MyPath, volumes_mock
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.fs import FileSystemContentReader, \
    FileSystemDirReader, TopTrashDirRulesFileSystemReader
from trashcli.fstab import VolumesListing


class TestEmptyCmdWithMultipleVolumes(unittest.TestCase):
    def setUp(self):
        self.temp_dir = MyPath.make_temp_dir()
        self.top_dir = self.temp_dir / 'topdir'
        self.volumes_listing = Mock(spec=VolumesListing)
        self.volumes_listing.list_volumes.return_value = [self.top_dir]
        require_empty_dir(self.top_dir)
        self.environ = {}
        self.empty_cmd = EmptyCmd(
            argv0='trash-empty',
            out=StringIO(),
            err=StringIO(),
            volumes_listing=self.volumes_listing,
            now=None,
            file_reader=TopTrashDirRulesFileSystemReader(),
            file_remover=ExistingFileRemover(),
            content_reader=FileSystemContentReader(),
            dir_reader=FileSystemDirReader(),
            version='unused',
            volumes=volumes_mock(),
        )

    def test_it_removes_trashinfos_from_method_1_dir(self):
        self.make_proper_top_trash_dir(self.top_dir / '.Trash')
        make_empty_file(self.top_dir / '.Trash/123/info/foo.trashinfo')

        self.empty_cmd.run_cmd([], self.environ, uid=123)

        assert not os.path.exists(
            self.top_dir / '.Trash/123/info/foo.trashinfo')

    def test_it_removes_trashinfos_from_method_2_dir(self):
        make_empty_file(self.top_dir / '.Trash-123/info/foo.trashinfo')

        self.empty_cmd.run_cmd([], self.environ, uid=123)

        assert not os.path.exists(
            self.top_dir / '.Trash-123/info/foo.trashinfo')

    def test_it_removes_trashinfo_from_specified_trash_dir(self):
        make_empty_file(self.temp_dir / 'specified/info/foo.trashinfo')

        self.empty_cmd.run_cmd(['--trash-dir', self.temp_dir / 'specified'],
                               self.environ, uid=123)

        assert not os.path.exists(
            self.temp_dir / 'specified/info/foo.trashinfo')

    @staticmethod
    def make_proper_top_trash_dir(path):
        make_dirs(path)
        set_sticky_bit(path)

    def tearDown(self):
        self.temp_dir.clean_up()
