import os
import unittest

from tests.support.run.run_command import run_command
from tests.support.fakes.fake_trash_dir import FakeTrashDir
from tests.support.files import make_file
from tests.support.list_trash_dir import list_trash_dir
from tests.support.my_path import MyPath


class TestEmptyEndToEndWithTrashDir(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.trash_dir = self.tmp_dir / 'trash-dir'
        self.fake_trash_dir = FakeTrashDir(self.trash_dir)

    def test_add_trashed_file(self):
        self.fake_trash_dir.add_trashed_file('foo', '/foo', 'FOO')

        assert list_trash_dir(self.trash_dir) == ['info/foo.trashinfo',
                                                  'files/foo']

    def test_trash_dir(self):
        self.fake_trash_dir.add_trashed_file('foo', '/foo', 'FOO')

        result = run_command(self.tmp_dir,
                             "trash-empty", ['--trash-dir', self.trash_dir])

        assert [result.all, list_trash_dir(self.trash_dir)] == \
               [('', '', 0), []]

    def test_xdg_data_home(self):
        xdg_data_home = self.tmp_dir / 'xdg'
        FakeTrashDir(xdg_data_home / 'Trash').add_trashed_file('foo', '/foo',
                                                               'FOO')

        result = run_command(self.tmp_dir, "trash-empty", [],
                             env={'XDG_DATA_HOME': xdg_data_home})

        trash_dir = xdg_data_home / 'Trash'
        assert [result.all, list_trash_dir(trash_dir)] == \
               [('', '', 0), []]

    def test_non_trash_info_is_not_deleted(self):
        make_file(self.trash_dir / 'info' / 'non-trashinfo')

        result = run_command(self.tmp_dir,
                             "trash-empty",
                             ['--trash-dir',
                              self.trash_dir])

        assert [result.all, list_trash_dir(self.trash_dir)] == \
               [('', '', 0), ['info/non-trashinfo']]

    def test_orphan_are_deleted(self):
        make_file(self.trash_dir / 'files' / 'orphan')
        os.makedirs(self.trash_dir / 'files' / 'orphan dir')

        result = run_command(self.tmp_dir, "trash-empty",
                             ['--trash-dir', self.trash_dir])

        assert [result.all, list_trash_dir(self.trash_dir)] == \
               [('', '', 0), []]

    def tearDown(self):
        self.tmp_dir.clean_up()
