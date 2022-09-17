# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import unittest
from typing import cast

from mock import Mock
from six import StringIO

from tests.support import volumes_mock
from trashcli.empty.delete_according_date import ContentReader
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.fstab import VolumesListing
from trashcli.trash import DirReader
from trashcli.trash_dirs_scanner import TopTrashDirRules


class MockDirReader(DirReader):
    def __init__(self, dirs):
        self.dirs = dirs

    def entries_if_dir_exists(self, path):  # type: (str) -> list[str]
        return self.dirs[path]

    def exists(self, path):  # type: (str) -> bool
        raise NotImplementedError()


class MyMock:
    def __init__(self, funcs, cls):
        print(repr(dir(cls)))
        self.funcs = funcs
        self.cls = cls

    def cast(self):
        return cast(self.cls, self)



class TestTrashEmptyCmdFs(unittest.TestCase):
    def setUp(self):
        self.volumes_listing = MyMock(funcs=[], cls=VolumesListing)
        self.file_reader = Mock(spec=TopTrashDirRules.Reader, spec_set=[])
        self.file_remover = MyMock(funcs=[], cls=ExistingFileRemover)
        self.content_reader = Mock(spec=ContentReader, spec_set=[])
        self.dir_reader = MockDirReader({'/xdg/Trash/info': [
            'pippo.trashinfo'
        ],
            '/xdg/Trash/files': []})
        self.err = StringIO()
        self.out = StringIO()
        self.environ = {'XDG_DATA_HOME': '/xdg'}
        self.empty = EmptyCmd(
            argv0='trash-empty',
            out=self.out,
            err=self.err,
            volumes_listing=self.volumes_listing.cast(),
            now=None,
            file_reader=cast(TopTrashDirRules.Reader, self.file_reader),
            file_remover=self.file_remover.cast(),
            content_reader=cast(ContentReader, self.content_reader),
            dir_reader=cast(DirReader, self.dir_reader),
            version='unused',
            volumes=volumes_mock()
        )

    def test(self):
        self.empty.run_cmd([], self.environ, uid=123)
