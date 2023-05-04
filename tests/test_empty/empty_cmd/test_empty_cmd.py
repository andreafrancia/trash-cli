# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import unittest
from typing import cast

from flexmock import flexmock
from mock import Mock, call
from six import StringIO

from tests.mock_dir_reader import MockDirReader
from tests.support.fake_volume_of import volume_of_stub
from trashcli.empty.delete_according_date import ContentReader
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.fstab.volume_listing import VolumesListing
from trashcli.lib.dir_reader import DirReader
from trashcli.trash_dirs_scanner import TopTrashDirRules


class TestTrashEmptyCmdFs(unittest.TestCase):
    def setUp(self):
        self.volumes_listing = Mock(spec=VolumesListing)
        self.file_reader = flexmock(TopTrashDirRules.Reader)
        self.file_remover = Mock(spec=ExistingFileRemover)
        self.content_reader = flexmock(ContentReader)
        self.dir_reader = MockDirReader()
        self.err = StringIO()
        self.out = StringIO()
        self.environ = {'XDG_DATA_HOME': '/xdg'}
        self.empty = EmptyCmd(
            argv0='trash-empty',
            out=self.out,
            err=self.err,
            volumes_listing=cast(VolumesListing, self.volumes_listing),
            now=None,
            file_reader=cast(TopTrashDirRules.Reader, self.file_reader),
            file_remover=cast(ExistingFileRemover, self.file_remover),
            content_reader=cast(ContentReader, self.content_reader),
            dir_reader=cast(DirReader, self.dir_reader),
            version='unused',
            volumes=volume_of_stub()
        )

    def test(self):
        self.volumes_listing.list_volumes.return_value = []
        self.dir_reader.mkdir('/xdg')
        self.dir_reader.mkdir('/xdg/Trash')
        self.dir_reader.mkdir('/xdg/Trash/info')
        self.dir_reader.add_file('/xdg/Trash/info/pippo.trashinfo')
        self.dir_reader.mkdir('/xdg/Trash/files')

        self.empty.run_cmd([], self.environ, uid=123)

        assert self.file_remover.mock_calls == [
            call.remove_file_if_exists('/xdg/Trash/files/pippo'),
            call.remove_file_if_exists('/xdg/Trash/info/pippo.trashinfo')
        ]

    def test_with_dry_run(self):
        self.volumes_listing.list_volumes.return_value = []
        self.dir_reader.mkdir('/xdg')
        self.dir_reader.mkdir('/xdg/Trash')
        self.dir_reader.mkdir('/xdg/Trash/info')
        self.dir_reader.add_file('/xdg/Trash/info/pippo.trashinfo')
        self.dir_reader.mkdir('/xdg/Trash/files')

        self.empty.run_cmd(['--dry-run'], self.environ, uid=123)

        assert self.file_remover.mock_calls == []
        assert self.out.getvalue() == \
               'would remove /xdg/Trash/files/pippo\n' \
               'would remove /xdg/Trash/info/pippo.trashinfo\n'
