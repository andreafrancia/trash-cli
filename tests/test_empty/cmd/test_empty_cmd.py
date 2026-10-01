# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import unittest
from typing import cast

from six import StringIO

from tests.support.put.fake_fs.fake_fs import FakeFs
from tests.support.trash_dirs.given_trash import GivenTrash
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.empty.existing_file_remover import ExistingFileRemover
from tests.support.fake_fs.fake_volumes_listing import FakeVolumesListing


class TestTrashEmptyCmdFs(unittest.TestCase):
    def setUp(self):
        self.fs = FakeFs()
        self.trash = GivenTrash(self.fs)
        self.err = StringIO()
        self.out = StringIO()
        self.environ = {'XDG_DATA_HOME': '/xdg'}
        self.empty = EmptyCmd(
            argv0='trash-empty',
            out=self.out,
            err=self.err,
            volumes_listing=FakeVolumesListing(),
            now=None,
            file_reader=self.fs,
            file_remover=cast(ExistingFileRemover, self.fs),
            content_reader=self.fs,
            dir_reader=self.fs,
            version='unused',
            volumes=self.fs
        )
        self.trash.has_file('/xdg/Trash/info/pippo.trashinfo')
        self.trash.has_file('/xdg/Trash/files/pippo')

    def test(self):
        self.empty.run_cmd([], self.environ, uid=123)

        assert self.fs.listdir('/xdg/Trash/files') == []
        assert self.fs.listdir('/xdg/Trash/info') == []

    def test_with_dry_run(self):
        self.empty.run_cmd(['--dry-run'], self.environ, uid=123)

        assert self.fs.listdir('/xdg/Trash/files') == ['pippo']
        assert self.fs.listdir('/xdg/Trash/info') == ['pippo.trashinfo']
        assert self.out.getvalue() == \
               'would remove /xdg/Trash/files/pippo\n' \
               'would remove /xdg/Trash/info/pippo.trashinfo\n'
