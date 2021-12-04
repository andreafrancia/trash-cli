# Copyright (C) 2011-2021 Andrea Francia Bereguardo(PV) Italy
import unittest

import pytest

from trashcli.empty import EmptyCmd
from mock import Mock
from six import StringIO
import os

from trashcli.fstab import VolumesListing
from .files import require_empty_dir, make_dirs, set_sticky_bit, \
    make_unreadable_dir, make_empty_file, make_readable
from .support import MyPath
from trashcli.fs import FileSystemReader
from trashcli.fs import FileRemover


@pytest.mark.slow
class TestTrashEmptyCmd(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.unreadable_dir = self.tmp_dir / 'data/Trash/files/unreadable'
        self.volumes_listing = Mock(spec=VolumesListing)
        self.volumes_listing.list_volumes.return_value = [self.unreadable_dir]
        self.err=StringIO()
        self.empty = EmptyCmd(
            out=StringIO(),
            err=self.err,
            environ={'XDG_DATA_HOME':self.tmp_dir / 'data'},
            volumes_listing=self.volumes_listing,
            now=None,
            file_reader=FileSystemReader(),
            getuid=lambda: 123,
            file_remover=FileRemover(),
            version=None,
            volume_of=lambda x: "volume_of %s" % x
        )

    def test_trash_empty_will_skip_unreadable_dir(self):
        make_unreadable_dir(self.unreadable_dir)

        self.empty.run('trash-empty')

        assert ("trash-empty: cannot remove %s\n"  % self.unreadable_dir ==
                     self.err.getvalue())

    def tearDown(self):
        make_readable(self.unreadable_dir)
        self.tmp_dir.clean_up()


class TestEmptyCmdWithMultipleVolumes(unittest.TestCase):
    def setUp(self):
        self.temp_dir = MyPath.make_temp_dir()
        self.top_dir = self.temp_dir / 'topdir'
        self.volumes_listing = Mock(spec=VolumesListing)
        self.volumes_listing.list_volumes.return_value = [self.top_dir]
        require_empty_dir(self.top_dir)
        self.empty = EmptyCmd(
            out=StringIO(),
            err=StringIO(),
            environ={},
            volumes_listing=self.volumes_listing,
            now=None,
            file_reader=FileSystemReader(),
            getuid=lambda: 123,
            file_remover=FileRemover(),
            version=None,
            volume_of=lambda x: "volume_of %s" % x
        )

    def test_it_removes_trashinfos_from_method_1_dir(self):
        self.make_proper_top_trash_dir(self.top_dir / '.Trash')
        make_empty_file(self.top_dir / '.Trash/123/info/foo.trashinfo')

        self.empty.run('trash-empty')

        assert not os.path.exists(
            self.top_dir / '.Trash/123/info/foo.trashinfo')
    def test_it_removes_trashinfos_from_method_2_dir(self):
        make_empty_file(self.top_dir / '.Trash-123/info/foo.trashinfo')

        self.empty.run('trash-empty')

        assert not os.path.exists(
            self.top_dir / '.Trash-123/info/foo.trashinfo')

    def test_it_removes_trashinfo_from_specified_trash_dir(self):
        make_empty_file(self.temp_dir / 'specified/info/foo.trashinfo')

        self.empty.run('trash-empty', '--trash-dir',
                       self.temp_dir / 'specified')

        assert not os.path.exists(
            self.temp_dir / 'specified/info/foo.trashinfo')


    def make_proper_top_trash_dir(self, path):
        make_dirs(path)
        set_sticky_bit(path)

    def tearDown(self):
        self.temp_dir.clean_up()
