import os
import unittest

from tests.support.dirs.my_path import MyPath
from tests.support.fs_fixture import FsFixture
from tests.support.run.run_command import run_command
from tests.support.trash_dirs.fake_trash_dir import FakeTrashDir
from trashcli.put.fs.real_fs import RealFs


class TestEmptyEndToEndWithTrashDir(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.trash_dir = self.tmp_dir / 'trash-dir'
        self.fake_trash_dir = FakeTrashDir(self.trash_dir)
        self.fs = RealFs()
        self.fx = FsFixture(self.fs)

    def test_add_trashed_file(self):
        self.fake_trash_dir.add_trashed_file('foo', '/foo', b'FOO')

        assert self.fake_trash_dir.list_trash_dir() == ['info/foo.trashinfo',
                                                        'files/foo']

    def test_trash_dir(self):
        self.fake_trash_dir.add_trashed_file('foo', '/foo', b'FOO')

        result = run_command(self.tmp_dir,
                             "trash-empty", ['--trash-dir', self.trash_dir])

        assert [result.all, self.fake_trash_dir.list_trash_dir()] == \
               [('', '', 0), []]

    def test_xdg_data_home(self):
        xdg_data_home = self.tmp_dir / 'xdg'
        fake_trash_dir = FakeTrashDir(xdg_data_home / 'Trash')
        fake_trash_dir.add_trashed_file('foo', '/foo', b'FOO')

        result = run_command(self.tmp_dir, "trash-empty", [],
                             env={'XDG_DATA_HOME': xdg_data_home})

        trash_dir = xdg_data_home / 'Trash'
        assert [result.all, fake_trash_dir.list_trash_dir()] == \
               [('', '', 0), []]

    def test_non_trash_info_is_not_deleted(self):
        self.fx.make_empty_file(self.trash_dir / 'info' / 'non-trashinfo')

        result = run_command(self.tmp_dir,
                             "trash-empty",
                             ['--trash-dir',
                              self.trash_dir])

        assert [result.all, self.fake_trash_dir.list_trash_dir()] == \
               [('', '', 0), ['info/non-trashinfo']]

    def test_orphan_are_deleted(self):
        self.fx.make_empty_file(self.trash_dir / 'files' / 'orphan')
        os.makedirs(self.trash_dir / 'files' / 'orphan dir')

        result = run_command(self.tmp_dir, "trash-empty",
                             ['--trash-dir', self.trash_dir])

        assert [result.all, self.fake_trash_dir.list_trash_dir()] == \
               [('', '', 0), []]

    def tearDown(self):
        self.tmp_dir.clean_up()
