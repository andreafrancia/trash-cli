# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import unittest

import pytest
from mock import Mock
from six import StringIO

from tests.files import make_unreadable_dir, make_readable
from tests.support import MyPath, volumes_mock
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.fs import FileSystemContentReader, \
    FileSystemDirReader, TopTrashDirRulesFileSystemReader
from trashcli.fstab import VolumesListing


@pytest.mark.slow
class TestTrashEmptyCmd(unittest.TestCase):
    def setUp(self):
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
            file_reader=TopTrashDirRulesFileSystemReader(),
            file_remover=ExistingFileRemover(),
            content_reader=FileSystemContentReader(),
            dir_reader=FileSystemDirReader(),
            version='unused',
            volumes=volumes_mock()
        )

    def test_trash_empty_will_skip_unreadable_dir(self):
        make_unreadable_dir(self.unreadable_dir)

        self.empty.run_cmd([], self.environ, uid=123)

        assert ("trash-empty: cannot remove %s\n" % self.unreadable_dir ==
                self.err.getvalue())

    def tearDown(self):
        make_readable(self.unreadable_dir)
        self.tmp_dir.clean_up()
