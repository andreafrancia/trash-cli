import datetime
import os
import unittest

import pytest
from mock import MagicMock
from six import StringIO

from . import no_volumes
from ..fake_trash_dir import FakeTrashDir
from ..files import require_empty_dir, make_file
from trashcli.empty import EmptyCmd
from trashcli.fs import FileSystemReader, FileRemover, read_file
from ..support import MyPath
from .. import run_command


@pytest.mark.slow
class TestWhen_invoked_with_N_days_as_argument(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.xdg_data_home = self.tmp_dir / 'XDG_DATA_HOME'
        require_empty_dir(self.xdg_data_home)
        self.environ = {'XDG_DATA_HOME': self.xdg_data_home}
        self.now = MagicMock(side_effect=RuntimeError)
        self.trash_dir = self.xdg_data_home / 'Trash'
        self.fake_trash_dir = FakeTrashDir(self.trash_dir)
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
        def date(yyyy_mm_dd):
            from datetime import datetime
            return datetime.strptime(yyyy_mm_dd, '%Y-%m-%d')
        self.now.side_effect = lambda: date(yyyy_mm_dd)
        self.environ['TRASH_DATE'] = '%sT00:00:00' % yyyy_mm_dd

    def test_set_clock(self):
        self.set_clock_at('2000-01-01')

        result = run_command.run_command(self.tmp_dir, "trash-empty",
                                         ['--print-time'], env=self.environ)

        self.assertEqual(['2000-01-01T00:00:00\n', '', 0], result.all)

    def test_it_should_keep_files_newer_than_N_days(self):
        self.fake_trash_dir.add_trashinfo_with_date('foo', datetime.date(2000, 1, 1))
        self.set_clock_at('2000-01-01')

        self.user_run_trash_empty('2')

        assert self.list_trash() == ['foo.trashinfo']

    def test_it_should_remove_files_older_than_N_days(self):
        self.fake_trash_dir.add_trashinfo_with_date('foo', datetime.date(1999, 1, 1))
        self.set_clock_at('2000-01-01')

        self.user_run_trash_empty('2')

        assert self.list_trash() == []

    def test_it_should_kept_files_with_invalid_deletion_date(self):
        self.fake_trash_dir.add_trashinfo_with_invalid_date('foo', 'Invalid Date')
        self.set_clock_at('2000-01-01')

        self.user_run_trash_empty('2')

        assert self.list_trash() == ['foo.trashinfo']

    def list_trash(self):
        return os.listdir(self.trash_dir / 'info')

