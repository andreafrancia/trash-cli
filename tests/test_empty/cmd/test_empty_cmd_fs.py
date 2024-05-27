# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import unittest

import pytest
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


@pytest.mark.slow
class TestTrashEmptyCmdFs(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.unreadable_dir = self.tmp_dir / 'data/Trash/files/unreadable'
        self.err = StringIO()
        self.environ = {'XDG_DATA_HOME': self.tmp_dir / 'data'}
        self.empty = EmptyCmd(
            argv0='trash-empty',
            out=StringIO(),
            err=self.err,
            now=None,
            file_reader=RealTopTrashDirRulesReader(),
            file_remover=ExistingFileRemover(),
            content_reader=FileSystemContentReader(),
            dir_reader=FileSystemDirReader(),
            version='unused',
            volumes=StubVolumeOf(),
            mount_point_listing=FakeMountPointsListing([self.unreadable_dir]),
        )
        self.fx = FsFixture(RealFs())

    def test_trash_empty_will_skip_unreadable_dir(self):
        self.fx.make_unreadable_dir(self.unreadable_dir)

        self.empty.run_cmd([], self.environ, uid=123)

        assert ("trash-empty: cannot remove %s\n" % self.unreadable_dir ==
                self.err.getvalue())

    def tearDown(self):
        self.fx.make_readable(self.unreadable_dir)
        self.tmp_dir.clean_up()
