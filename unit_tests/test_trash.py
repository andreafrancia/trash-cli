# Copyright (C) 2007-2011 Andrea Francia Trivolzio(PV) Italy

from __future__ import absolute_import

__author__="Andrea Francia (andrea.francia@users.sourceforge.net)"
__copyright__="Copyright (c) 2007 Andrea Francia"
__license__="GPL"

from trashcli.trash import TrashDirectory
from trashcli.trash import TrashedFile
from trashcli.trash import TrashInfo
from trashcli.trash import TimeUtils

from datetime import datetime
import os
from unittest import TestCase
from nose.tools import raises
from nose.tools import assert_equals
abspath = os.path.abspath
import shutil

class TestTrashDirectory(TestCase) :

    def test_calc_id(self):
        trash_info_file = "/home/user/.local/share/Trash/info/foo.trashinfo"
        self.assertEquals('foo',TrashDirectory.calc_id(trash_info_file))

    def test_calc_original_location_when_absolute(self) :
        trash_dir = TrashDirectory( "/mnt/disk/.Trash-123", "/mnt/disk")

        assert_equals("/foo", trash_dir._calc_original_location("/foo"))

    def test_calc_original_location_when_relative(self) :
        trash_dir = TrashDirectory( "/mnt/disk/.Trash-123", "/mnt/disk")

        assert_equals("/mnt/disk/foo", trash_dir._calc_original_location("foo"))

class TestTrashInfo(TestCase) :
    def test_parse(self) :
        data = """[Trash Info]
Path=home%2Fandrea%2Fprova.txt
DeletionDate=2007-07-23T23:45:07"""
        result = TrashInfo.parse(data)
        self.assertEqual(result.path, "home/andrea/prova.txt")
        self.assert_(isinstance(result.deletion_date,datetime))
        self.assertEqual(result.deletion_date,
                         datetime(2007, 7, 23, 23, 45, 07))

    def test_init(self) :
        instance = TrashInfo("path", datetime(2007, 7, 23, 23, 45, 07))
        self.assertEquals("path", instance.path)
        self.assertEquals(datetime(2007, 7, 23, 23, 45, 07), instance.deletion_date)

    def test_init2(self) :
        instance = TrashInfo("path", datetime(2007, 7, 23, 23, 45, 07))
        self.assertEquals("path", instance.path)
        self.assertEquals(datetime(2007, 7, 23, 23, 45, 07), instance.deletion_date)

    def test_format_date(self) :
        date = datetime(2007, 7, 23, 23, 45, 07)
        self.assertEquals("2007-07-23T23:45:07", TrashInfo._format_date(date))


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

    @raises(ValueError)
    def test_init_requires_absolute_paths(self):
        path = "./relative-path"
        deletion_date = datetime(2001,01,01)
        info_file = "/home/user/.local/share/Trash/info/foo.trashinfo"
        actual_path = "/home/user/.local/share/Trash/files/foo"
        trash_directory = TrashDirectory('/home/user/.local/share/Trash', '/')

        TrashedFile(path, deletion_date, info_file, actual_path,
                    trash_directory)


    def test_restore_create_needed_directories(self):
        trash_dir = TrashDirectory(self.xdg_data_home, '/')
        trash_dir.store_absolute_paths()
        os.mkdir("sandbox/foo")
        touch("sandbox/foo/bar")
        instance = trash_dir.trash("sandbox/foo/bar")
        shutil.rmtree("sandbox/foo")
        instance.restore()
        assert os.path.exists("sandbox/foo/bar")

class TestTimeUtils(TestCase) :
    def test_parse_iso8601(self) :
        expected=datetime(2008,9,8,12,00,11)
        result=TimeUtils.parse_iso8601("2008-09-08T12:00:11")
        self.assertEqual(expected,result)

def touch(path):
    open(path, 'a+').close()
