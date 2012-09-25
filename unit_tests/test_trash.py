# Copyright (C) 2007-2011 Andrea Francia Trivolzio(PV) Italy

from __future__ import absolute_import

from trashcli.trash import TrashDirectory
from trashcli.trash import TrashedFile
from integration_tests.files import write_file, require_empty_dir

import os
from unittest import TestCase
from nose.tools import assert_equals
abspath = os.path.abspath

from datetime import datetime
class TestTrashedFile(TestCase) :
    __dummy_datetime=datetime(2007, 7, 23, 23, 45, 07)
    def setUp(self):
        self.xdg_data_home = ("sandbox/XDG_DATA_HOME")

    def test_init(self) :
        path = "/foo"
        deletion_date = datetime(2001,01,01)
        info_file = "/home/user/.local/share/Trash/info/foo.trashinfo"
        actual_path = ("/home/user/.local/share/Trash/files/foo")
        trash_directory = TrashDirectory('/home/user/.local/share/Trash', '/')

        instance = TrashedFile(path, deletion_date, info_file, actual_path,
                              trash_directory)

        assert_equals(instance.path, path)
        assert_equals(instance.deletion_date, deletion_date)
        assert_equals(instance.info_file, info_file)
        assert_equals(instance.actual_path, actual_path)
        assert_equals(trash_directory, trash_directory)

    def test_restore_create_needed_directories(self):
        require_empty_dir('sandbox')

        write_file('sandbox/TrashDir/files/bar')
        instance = TrashedFile('sandbox/foo/bar',
                               'deletion_date', 'info_file',
                               'sandbox/TrashDir/files/bar', 'trash_dirctory')
        instance.restore()
        assert os.path.exists("sandbox/foo/bar")

def touch(path):
    open(path, 'a+').close()
