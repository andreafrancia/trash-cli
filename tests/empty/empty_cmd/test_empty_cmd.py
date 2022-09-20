# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import unittest
from typing import cast

from six import StringIO

from tests.mock_dir_reader import MockDirReader
from tests.support import volumes_mock
from trashcli.empty.delete_according_date import ContentReader
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.fstab import VolumesListing
from trashcli.trash import DirReader
from trashcli.trash_dirs_scanner import TopTrashDirRules

from flexmock import flexmock


class TestTrashEmptyCmdFs(unittest.TestCase):
    def setUp(self):
        self.volumes_listing = flexmock(VolumesListing)
        self.file_reader = flexmock(TopTrashDirRules.Reader)
        self.file_remover = flexmock(ExistingFileRemover)
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
            volumes=volumes_mock()
        )

    def test(self):
        flexmock(self.file_remover). \
            should_receive('remove_file_if_exists'). \
            with_args('/xdg/Trash/info/pippo.trashinfo').once()
        flexmock(self.file_remover). \
            should_receive('remove_file_if_exists'). \
            with_args("/xdg/Trash/files/pippo").once()
        flexmock(self.volumes_listing). \
            should_receive('list_volumes'). \
            and_return([]).once()

        self.dir_reader.mkdir('/xdg')
        self.dir_reader.mkdir('/xdg/Trash')
        self.dir_reader.mkdir('/xdg/Trash/info')
        self.dir_reader.add_file('/xdg/Trash/info/pippo.trashinfo')
        self.dir_reader.mkdir('/xdg/Trash/files')

        self.empty.run_cmd([], self.environ, uid=123)
