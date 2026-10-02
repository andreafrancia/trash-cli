# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import unittest

from six import StringIO

from tests.support.dirs.my_path import MyPath
from trashcli.fslib.real.real_fs import RealFs
from tests.support.trash_dirs.given_trash import GivenTrash
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.empty.file_system_dir_reader import FileSystemDirReader
from tests.support.fake_fs.fake_volumes_listing import FakeVolumesListing


class TestTrashEmptyCmdReal(unittest.TestCase):
    def setUp(self):
        self.fs = RealFs()
        self.tmp_dir = MyPath.make_temp_dir()
        self.xdg = str(self.tmp_dir / 'xdg')
        self.trash = GivenTrash(self.fs)
        self.err = StringIO()
        self.out = StringIO()
        self.environ = {'XDG_DATA_HOME': self.xdg}
        self.empty = EmptyCmd(
            argv0='trash-empty',
            out=self.out,
            err=self.err,
            volumes_listing=FakeVolumesListing(),
            now=None,
            file_reader=self.fs,
            file_remover=ExistingFileRemover(self.fs),
            content_reader=self.fs,
            dir_reader=FileSystemDirReader(self.fs),
            version='unused',
            volumes=self.fs
        )
        self.trash.has_file(self.xdg + '/Trash/info/pippo.trashinfo', '')
        self.trash.has_file(self.xdg + '/Trash/files/pippo', '')

    def test(self):
        self.empty.run_cmd([], self.environ, uid=123)

        assert self.fs.listdir(self.xdg + '/Trash/files') == []
        assert self.fs.listdir(self.xdg + '/Trash/info') == []

    def test_with_dry_run(self):
        self.empty.run_cmd(['--dry-run'], self.environ, uid=123)

        assert self.fs.listdir(self.xdg + '/Trash/files') == ['pippo']
        assert self.fs.listdir(self.xdg + '/Trash/info') == ['pippo.trashinfo']
        assert self.out.getvalue() == \
               'would remove %s/Trash/files/pippo\n' \
               'would remove %s/Trash/info/pippo.trashinfo\n' % (
                   self.xdg, self.xdg)

    def tearDown(self):
        self.tmp_dir.clean_up()
