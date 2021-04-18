import os
import unittest

import pytest
from mock import MagicMock
from six import StringIO

from . import no_volumes
from ..files import require_empty_dir, make_file
from trashcli.empty import EmptyCmd
from trashcli.fs import FileSystemReader, FileRemover
from ..support import MyPath


@pytest.mark.slow
class TestWhen_invoked_with_N_days_as_argument(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.xdg_data_home = self.tmp_dir / 'XDG_DATA_HOME'
        require_empty_dir(self.xdg_data_home)
        self.environ = {'XDG_DATA_HOME': self.xdg_data_home}
        self.now = MagicMock(side_effect=RuntimeError)
        self.empty_cmd = EmptyCmd(
            out=StringIO(),
            err=StringIO(),
            environ=self.environ,
            list_volumes=no_volumes,
            now=self.now,
            file_reader=FileSystemReader(),
            getuid=None,
            file_remover=FileRemover(),
            version=None,
        )

    def user_run_trash_empty(self, *args):
        self.empty_cmd.run('trash-empty', *args)

    def set_clock_at(self, yyyy_mm_dd):
        self.now.side_effect = lambda: date(yyyy_mm_dd)

        def date(yyyy_mm_dd):
            from datetime import datetime
            return datetime.strptime(yyyy_mm_dd, '%Y-%m-%d')

    def test_it_should_keep_files_newer_than_N_days(self):
        self.having_a_trashed_file('foo', '2000-01-01')
        self.set_clock_at('2000-01-01')

        self.user_run_trash_empty('2')

        self.file_should_have_been_kept_in_trashcan('foo')

    def test_it_should_remove_files_older_than_N_days(self):
        self.having_a_trashed_file('foo', '1999-01-01')
        self.set_clock_at('2000-01-01')

        self.user_run_trash_empty('2')

        self.file_should_have_been_removed_from_trashcan('foo')

    def test_it_should_kept_files_with_invalid_deletion_date(self):
        self.having_a_trashed_file('foo', 'Invalid Date')
        self.set_clock_at('2000-01-01')

        self.user_run_trash_empty('2')

        self.file_should_have_been_kept_in_trashcan('foo')

    def having_a_trashed_file(self, name, date):
        contents = "DeletionDate=%sT00:00:00\n" % date
        make_file(self.trashinfo(name), contents)

    def trashinfo(self, name):
        return '%(dirname)s/Trash/info/%(name)s.trashinfo' % {
            'dirname': self.xdg_data_home,
            'name': name}

    def file_should_have_been_kept_in_trashcan(self, trashinfo_name):
        assert os.path.exists(self.trashinfo(trashinfo_name))

    def file_should_have_been_removed_from_trashcan(self, trashinfo_name):
        assert not os.path.exists(self.trashinfo(trashinfo_name))
