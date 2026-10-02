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


class TestTrashEmptyCmdFakeFs(unittest.TestCase):
    def setUp(self):
        self.fs = FakeFs()
        self.fsx = FsFixture(self.fs)
        self.tmp_dir = '/tmp'
        self.unreadable_dir = self.tmp_dir + '/data/Trash/files/unreadable'
        self.volumes_listing = Mock(spec=VolumesListing)
        self.volumes_listing.list_volumes.return_value = [self.unreadable_dir]
        self.err = StringIO()
        self.environ = {'XDG_DATA_HOME': self.tmp_dir + '/data'}
        self.empty = EmptyCmd(
            argv0='trash-empty',
            out=StringIO(),
            err=self.err,
            volumes_listing=self.volumes_listing,
            now=None,
            file_reader=self.fs,
            file_remover=ExistingFileRemover(self.fs),
            content_reader=self.fs,
            dir_reader=FileSystemDirReader(self.fs),
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
