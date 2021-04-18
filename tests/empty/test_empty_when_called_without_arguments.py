# Copyright (C) 2011-2021 Andrea Francia Bereguardo(PV) Italy
import os
import unittest

import pytest
import six
from six import StringIO

from . import no_volumes
from ..files import require_empty_dir, make_empty_file, assert_dir_empty, assert_dir_contains
from trashcli.empty import EmptyCmd
from trashcli.fs import FileSystemReader, FileRemover
from ..support import MyPath
from mock import MagicMock


@pytest.mark.slow
class TestEmptyWhenCalledWithoutArguments(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.XDG_DATA_HOME = self.tmp_dir / 'XDG_DATA_HOME'
        require_empty_dir(self.XDG_DATA_HOME)
        self.info_dir_path = self.XDG_DATA_HOME / 'Trash/info'
        self.files_dir_path = self.XDG_DATA_HOME / 'Trash/files'
        self.environ = {'XDG_DATA_HOME': self.XDG_DATA_HOME}
        now = MagicMock(side_effect=RuntimeError)
        self.empty_cmd = EmptyCmd(
            out=StringIO(),
            err=StringIO(),
            environ=self.environ,
            list_volumes=no_volumes,
            now=now,
            file_reader=FileSystemReader(),
            getuid=None,
            file_remover=FileRemover(),
            version=None,
        )

    def user_run_trash_empty(self):
        self.empty_cmd.run('trash-empty')

    def test_it_should_remove_an_info_file(self):
        self.having_a_trashinfo_in_trashcan('foo.trashinfo')

        self.user_run_trash_empty()

        assert_dir_empty(self.info_dir_path)

    def test_it_should_remove_all_the_infofiles(self):
        self.having_three_trashinfo_in_trashcan()

        self.user_run_trash_empty()

        assert_dir_empty(self.info_dir_path)

    def test_it_should_remove_the_backup_files(self):
        self.having_one_trashed_file()

        self.user_run_trash_empty()

        assert_dir_empty(self.files_dir_path)

    def test_it_should_keep_unknown_files_found_in_infodir(self):
        self.having_file_in_info_dir('not-a-trashinfo')

        self.user_run_trash_empty()

        assert_dir_contains(self.info_dir_path, 'not-a-trashinfo')

    def test_but_it_should_remove_orphan_files_from_the_files_dir(self):
        self.having_orphan_file_in_files_dir()

        self.user_run_trash_empty()

        assert_dir_empty(self.files_dir_path)

    def test_it_should_purge_also_directories(self):
        os.makedirs(self.XDG_DATA_HOME / "Trash/files/a-dir")

        self.user_run_trash_empty()

        assert_dir_empty(self.files_dir_path)

    def having_a_trashinfo_in_trashcan(self, basename_of_trashinfo):
        make_empty_file(os.path.join(self.info_dir_path, basename_of_trashinfo))

    def having_three_trashinfo_in_trashcan(self):
        self.having_a_trashinfo_in_trashcan('foo.trashinfo')
        self.having_a_trashinfo_in_trashcan('bar.trashinfo')
        self.having_a_trashinfo_in_trashcan('baz.trashinfo')
        six.assertCountEqual(self,
                             ['foo.trashinfo',
                              'bar.trashinfo',
                              'baz.trashinfo'], os.listdir(self.info_dir_path))

    def having_one_trashed_file(self):
        self.having_a_trashinfo_in_trashcan('foo.trashinfo')
        make_empty_file(self.files_dir_path + '/foo')
        self.files_dir_should_not_be_empty()

    def files_dir_should_not_be_empty(self):
        assert len(os.listdir(self.files_dir_path)) != 0

    def having_file_in_info_dir(self, filename):
        make_empty_file(os.path.join(self.info_dir_path, filename))

    def having_orphan_file_in_files_dir(self):
        complete_path = os.path.join(self.files_dir_path,
                                     'a-file-without-any-associated-trashinfo')
        make_empty_file(complete_path)
        assert os.path.exists(complete_path)

    def tearDown(self):
        self.tmp_dir.clean_up()