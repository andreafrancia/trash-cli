# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import os
import unittest

import pytest
from tests.support.py2mock import Mock
from six import StringIO

from tests.support.fake_fs.fake_volumes_listing import FakeVolumesListing
from tests.support.fakes.stub_volume_of import StubVolumeOfFs
from tests.support.files import FsFixture
from tests.support.dirs.my_path import MyPath
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.empty.file_system_dir_reader import FileSystemDirReader
from trashcli.fslib.real.real_fs import RealFs
from trashcli.fslib.protocols.volumes_listing import VolumesListing


@pytest.mark.slow
class TestTrashEmptyCmdFs(unittest.TestCase):
    def setUp(self):
        self.fsx = FsFixture(RealFs())
        self.tmp_dir = MyPath.make_temp_dir()
        self.unreadable_dir = self.tmp_dir / 'data/Trash/files/unreadable'
        self.volumes_listing = Mock(spec=VolumesListing)
        self.volumes_listing.list_volumes.return_value = [self.unreadable_dir]
        self.err = StringIO()
        self.environ = {'XDG_DATA_HOME': self.tmp_dir / 'data'}
        self.empty = EmptyCmd(
            argv0='trash-empty',
            out=StringIO(),
            err=self.err,
            volumes_listing=self.volumes_listing,
            now=None,
            file_reader=RealFs(),
            file_remover=ExistingFileRemover(RealFs()),
            content_reader=RealFs(),
            dir_reader=FileSystemDirReader(RealFs()),
            version='unused',
            volumes=StubVolumeOfFs()
        )

    def test_trash_empty_will_skip_unreadable_dir(self):
        self.fsx.make_unreadable_dir(self.unreadable_dir)

        self.empty.run_cmd([], self.environ, uid=123)

        assert ("trash-empty: cannot remove %s\n" % self.unreadable_dir ==
                self.err.getvalue())

    def tearDown(self):
        self.fsx.make_readable(self.unreadable_dir)
        self.tmp_dir.clean_up()


@pytest.mark.slow
class TestTrashEmptyRemovesReadonlyDir:
    def setup_method(self):
        self.fs = RealFs()
        self.tmp_dir = MyPath.make_temp_dir()
        self.trash_files = self.tmp_dir / 'data/Trash/files'
        self.err = StringIO()
        self.environ = {'XDG_DATA_HOME': self.tmp_dir / 'data'}
        self.empty = EmptyCmd(
            argv0='trash-empty',
            out=StringIO(),
            err=self.err,
            volumes_listing=FakeVolumesListing(),
            now=None,
            file_reader=self.fs,
            file_remover=ExistingFileRemover(self.fs),
            content_reader=self.fs,
            dir_reader=FileSystemDirReader(self.fs),
            version='unused',
            volumes=StubVolumeOfFs()
        )

    def test_a_directory_without_write_permission_is_removed(self):
        target = self.trash_files / 'proj'
        self.fs.makedirs(target / 'sub', 0o755)
        self.fs.write_file(target / 'sub' / 'f', 'x')
        self.fs.chmod(target / 'sub', 0o500)
        self.fs.chmod(target, 0o500)

        self.empty.run_cmd([], self.environ, uid=123)

        assert not self.fs.path_exists(target)
        assert self.err.getvalue() == ""

    def teardown_method(self):
        # restore write bits so a failed run can still be cleaned up
        for root, dirs, files in self.fs.walk_no_follow(self.trash_files):
            for name in dirs:
                self.fs.chmod(os.path.join(root, name), 0o700)
        self.tmp_dir.clean_up()
