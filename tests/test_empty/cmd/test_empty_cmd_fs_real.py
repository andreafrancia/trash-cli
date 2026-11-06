# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import unittest

import pytest
from tests.support.py2mock import Mock
from six import StringIO

from tests.support.fakes.stub_volume_of import StubVolumeOfFs
from tests.support.files import FsFixture
from tests.support.dirs.temp_dir import make_temp_dir
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.empty.file_system_dir_reader import FileSystemDirReader
from trashcli.fslib.real.real_fs import RealFs
from trashcli.fslib.protocols.volumes_listing import VolumesListing


@pytest.mark.slow
class TestTrashEmptyCmdFs(unittest.TestCase):
    def setUp(self):
        self.fsx = FsFixture(RealFs())
        fs = RealFs()
        self.tmp_dir = make_temp_dir(fs)
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

    def test_trash_empty_removes_a_dir_containing_a_read_only_dir(self):
        # https://github.com/andreafrancia/trash-cli/issues/364
        trash = self.tmp_dir / 'data/Trash'
        self.fsx.fs.makedirs(trash + '/files/myfolder/testfolder', 0o755)
        self.fsx.fs.write_file(trash + '/files/myfolder/testfolder/file', 'a')
        self.fsx.fs.chmod(trash + '/files/myfolder/testfolder', 0o555)
        self.fsx.fs.makedirs(trash + '/info', 0o700)
        self.fsx.fs.write_file(trash + '/info/myfolder.trashinfo',
                           '[Trash Info]\nPath=/myfolder\n'
                           'DeletionDate=2000-01-01T00:00:00\n')

        self.empty.run_cmd([], self.environ, uid=123)

        assert self.fsx.fs.path_lexists(trash + '/files/myfolder') is False
        assert self.fsx.fs.path_lexists(trash + '/info/myfolder.trashinfo') is False
        assert self.err.getvalue() == ''

    def tearDown(self):
        if self.fsx.fs.path_exists(self.unreadable_dir):
            self.fsx.make_readable(self.unreadable_dir)
        self.tmp_dir.clean_up()
