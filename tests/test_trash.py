#!/usr/bin/python
# tests/test_trash.py: Unit tests for trashcli.trash module.
#
# Copyright (C) 2007-2009 Andrea Francia Trivolzio(PV) Italy
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  
# 02110-1301, USA.

from __future__ import absolute_import

"""
Unit test for Volume.py
"""

__author__="Andrea Francia (andrea.francia@users.sourceforge.net)"
__copyright__="Copyright (c) 2007 Andrea Francia"
__license__="GPL"

import sys

from trashcli.trash import TrashDirectory
from trashcli.trash import TrashedFile
from trashcli.trash import TrashInfo
from trashcli.trash import VolumeTrashDirectory
from trashcli.trash import TimeUtils
from trashcli.trash import HomeTrashDirectory
from trashcli.trash import GlobalTrashCan
from trashcli.filesystem import Path
from trashcli.filesystem import Volume
from trashcli.trash import TopDirIsSymLink
from trashcli.trash import TopDirNotPresent
from trashcli.trash import TopDirWithoutStickyBit
from trashcli.trash import Method1VolumeTrashDirectory

from datetime import *
from exceptions import *
import os
from unittest import TestCase
import pdb
import sys
from nose.tools import raises
from nose.tools import assert_equals

class TestTrashDirectory(TestCase) :
    def test_init(self) :
        path = Path("/mnt/disk/.Trash-123")
        volume = Volume(Path("/mnt/disk"), True);
        instance = TrashDirectory(path, volume)
        
        self.assertEquals(volume,instance.volume)
        self.assertEquals(path, instance.path)
        

    def test_trash(self) :
        #instance
        instance=VolumeTrashDirectory(
                        Path("sandbox/trash-directory"), 
                        Path("sandbox").volume)

        # test
        file_to_trash=Path("sandbox/dummy.txt")
        file_to_trash.touch()
        result = instance.trash(file_to_trash)
        self.assertTrue(isinstance(result,TrashedFile))
        self.assertEquals(file_to_trash.absolute(), result.path)
        self.assertTrue(result.deletion_date is not None)

    def test_get_info_dir(self):
        instance=TrashDirectory(
            Path("/mnt/disk/.Trash-123"),
            Volume(Path("/mnt/disk"), True))
        self.assertEquals("/mnt/disk/.Trash-123/info", instance.info_dir)

    def test_get_files_dir(self):
        instance=TrashDirectory(
            Path("/mnt/disk/.Trash-123"),
            Volume(Path("/mnt/disk"), True))
        self.assertEquals("/mnt/disk/.Trash-123/files", instance.files_dir)
    
    def test_calc_id(self):
        trash_info_file=Path("/home/user/.local/share/Trash/info/foo.trashinfo")
        self.assertEquals('foo',TrashDirectory.calc_id(trash_info_file))

    def test_calc_original_location_when_absolute(self) :
        instance = TrashDirectory(
            Path("/mnt/disk/.Trash-123"),
            Volume(Path("/mnt/disk"), True))
        
        assert_equals(Path("/foo"),
                      instance._calc_original_location(Path("/foo")))
        
    def test_calc_original_location_when_relative(self) :
        instance = TrashDirectory(
            Path("/mnt/disk/.Trash-123"),
            Volume(Path("/mnt/disk"), True))
        
        assert_equals(Path("/mnt/disk/foo"),
                      instance._calc_original_location(Path("foo")))
        
class TestTrashDirectory_persit_trash_info(TestCase) :
    def setUp(self):
        self.trashdirectory_base_dir = Path(os.path.realpath("./sandbox/testTrashDirectory"))
        self.trashdirectory_base_dir.remove()
        
        self.instance=TrashDirectory(self.trashdirectory_base_dir, Volume(Path("/")))
        
    def test_persist_trash_info_first_time(self):
        trash_info=TrashInfo(Path("dummy-path"), datetime(2007,01,01))

        (trash_info_file, trash_info_id)=self.instance.persist_trash_info(trash_info)

        self.assertTrue(isinstance(trash_info_file, Path))
        self.assertEquals('dummy-path', trash_info_id)
        self.assertEquals(self.trashdirectory_base_dir.join('info').join('dummy-path.trashinfo').path, trash_info_file)

        self.assertEquals("""[Trash Info]
Path=dummy-path
DeletionDate=2007-01-01T00:00:00
""", trash_info_file.read())
        
    def test_persist_trash_info_first_100_times(self):
        self.test_persist_trash_info_first_time()
        
        for i in range(1,100) :
            trash_info=TrashInfo(Path("dummy-path"), datetime(2007,01,01))
            
            (trash_info_file, trash_info_id)=self.instance.persist_trash_info(trash_info)
    
            self.assertTrue(isinstance(trash_info_id, str))
            self.assertEquals('dummy-path'+"_" + str(i), trash_info_id)
            self.assertEquals("""[Trash Info]
Path=dummy-path
DeletionDate=2007-01-01T00:00:00
""", trash_info_file.read())

    def test_persist_trash_info_other_times(self):
        self.test_persist_trash_info_first_100_times()
        
        for i in range(101,200) :
            trash_info=TrashInfo(Path("dummy-path"), datetime(2007,01,01))
            
            (trash_info_file, trash_info_id)=self.instance.persist_trash_info(trash_info)
    
            self.assertTrue(isinstance(trash_info_id, str))
            self.assertTrue(trash_info_id.startswith("dummy-path_"))
            self.assertEquals("""[Trash Info]
Path=dummy-path
DeletionDate=2007-01-01T00:00:00
""", trash_info_file.read())


       
class TestHomeTrashDirectory(TestCase) :
    def test_path_for_trashinfo (self) : 
        instance = HomeTrashDirectory(Path("/home/user/.local/share/Trash"))
        instance.volume = Volume(Path("/"))

        # path for HomeTrashDirectory are always absolute
        fileToBeTrashed=Path("/home/user/test.txt")
        result=instance._path_for_trashinfo(fileToBeTrashed)
        self.assertTrue(isinstance(result,Path))
        self.assertEquals("/home/user/test.txt",result)
            
        #  ... even if the file is under /home/user/.local/share
        fileToBeTrashed=Path("/home/user/.local/share/test.txt")
        result=instance._path_for_trashinfo(fileToBeTrashed)
        self.assertEquals(os.path.abspath("/home/user/.local/share/test.txt"),result)

    def test_str_uses_tilde(self):
        os.environ['HOME']='/home/user'
        self.assertEquals('~/.local/share/Trash', str(HomeTrashDirectory(Path("/home/user/.local/share/Trash"))))
                          
    def test_str_dont_uses_tilde(self):
        os.environ['HOME']='/home/user'        
        self.assertEquals('/not-in-home/Trash', str(HomeTrashDirectory(Path("/not-in-home/Trash"))))

    def test_str_uses_tilde_with_trailing_slashes(self):
        os.environ['HOME']='/home/user/'
        self.assertEquals('~/.local/share/Trash', str(HomeTrashDirectory(Path("/home/user/.local/share/Trash"))))

    def test_str_uses_tilde_with_trailing_slash(self):
        os.environ['HOME']='/home/user////'
        self.assertEquals('~/.local/share/Trash', str(HomeTrashDirectory(Path("/home/user/.local/share/Trash"))))

    def test_str_with_empty_home(self):
        os.environ['HOME']=''
        self.assertEquals('/foo/Trash', str(HomeTrashDirectory(Path("/foo/Trash"))))
                
    def test_str_with_home_not_defined(self):
        del(os.environ['HOME'])
        self.assertEquals('/foo/Trash', str(HomeTrashDirectory(Path("/foo/Trash"))))
                          
class TestVolumeTrashDirectory(TestCase) :
    def test_init(self) :
        path = Path("/mnt/disk/.Trash/123")
        volume = Volume(Path("/mnt/disk"), True)
        instance = VolumeTrashDirectory(path, volume)
        self.assertEquals(path, instance.path)
        self.assertEquals(volume, instance.volume)
        
    def test_path_for_trashinfo (self) : 
        path = Path("/mnt/disk/.Trash-123")
        volume = Volume(Path("/mnt/volume"), True)
        instance = VolumeTrashDirectory(path, volume)

        # path for VolumeTrashDirectory are relative as possible
        fileToBeTrashed=Path("/mnt/volume/directory/test.txt")
        result=instance._path_for_trashinfo(fileToBeTrashed)
        self.assertEquals("directory/test.txt",result)
            
        # path for VolumeTrashDirectory are relative as possible
        fileToBeTrashed=Path("/mnt/other-volume/directory/test.txt")
        result=instance._path_for_trashinfo(fileToBeTrashed)
        self.assertEquals("/mnt/other-volume/directory/test.txt",result)
                    
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
        instance = TrashInfo(Path("path"), datetime(2007, 7, 23, 23, 45, 07))
        self.assertEquals("path", instance.path)
        self.assertEquals(datetime(2007, 7, 23, 23, 45, 07), instance.deletion_date)

    def test_init2(self) :
        instance = TrashInfo(Path("path"), datetime(2007, 7, 23, 23, 45, 07))
        self.assertEquals("path", instance.path)
        self.assertEquals(datetime(2007, 7, 23, 23, 45, 07), instance.deletion_date)
    
    def test_format_date(self) :
        date = datetime(2007, 7, 23, 23, 45, 07)
        self.assertEquals("2007-07-23T23:45:07", TrashInfo._format_date(date))


class TestTrashedFile(TestCase) :
    __dummy_datetime=datetime(2007, 7, 23, 23, 45, 07)
    def setUp(self):
        self.xdg_data_home = Path("sandbox").join("XDG_DATA_HOME")
        
    def test_init(self) :
        path = Path("/foo")
        deletion_date = datetime(2001,01,01)
        info_file = Path("/home/user/.local/share/Trash/info/foo.trashinfo")
        actual_path = Path("/home/user/.local/share/Trash/files/foo")
        trash_directory = HomeTrashDirectory(
            Path('/home/user/.local/share/Trash'))
        
        instance = TrashedFile(path, deletion_date, info_file, actual_path, 
                              trash_directory)
        
        assert_equals(instance.path, path)
        assert_equals(instance.deletion_date, deletion_date)
        assert_equals(instance.info_file, info_file)
        assert_equals(instance.actual_path, actual_path)
        assert_equals(trash_directory, trash_directory)
    
    @raises(ValueError)
    def test_init_requires_absolute_paths(self):
        path = Path("./relative-path")
        deletion_date = datetime(2001,01,01)
        info_file = Path("/home/user/.local/share/Trash/info/foo.trashinfo")
        actual_path = Path("/home/user/.local/share/Trash/files/foo")
        trash_directory = HomeTrashDirectory(
            Path('/home/user/.local/share/Trash'))
        
        TrashedFile(path, deletion_date, info_file, actual_path, 
                    trash_directory)
    

    def test_restore_create_needed_directories(self):
        trash_dir = HomeTrashDirectory(self.xdg_data_home)
        Path("sandbox/foo").mkdir()
        Path("sandbox/foo/bar").touch()
        instance = trash_dir.trash(Path("sandbox/foo/bar"))
        Path("sandbox/foo").remove()
        instance.restore()
        assert Path("sandbox/foo/bar").exists() == True

class TestTimeUtils(TestCase) :
    def test_parse_iso8601(self) :
        expected=datetime(2008,9,8,12,00,11)
        result=TimeUtils.parse_iso8601("2008-09-08T12:00:11")
        self.assertEqual(expected,result)

class GlobalTrashCanTest(TestCase) :
    
    def testBasePath(self) :
        # prepare
        os.environ['HOME'] = "/home/test"
        instance = GlobalTrashCan()
        # execute 
        td = instance.home_trash_dir()
        # verify
        self.assertEqual(Path("/"), td.volume)

    def test_volume_trash_dir1(self) :
        # prepare
        instance = GlobalTrashCan(fake_uid=999)
        
        # execute
        result = instance.volume_trash_dir1(Volume(Path("/mnt/disk")))
        
        # check
        self.assert_(isinstance(result,TrashDirectory))
        self.assertEqual('/mnt/disk/.Trash/999', result.path.path)
    
    def test_volume_trash_dir2(self) :        
        # prepare
        instance = GlobalTrashCan(fake_uid=999)
        
        # execute
        result = instance.volume_trash_dir2(Volume(Path("/mnt/disk")))
        
        # check
        self.assert_(isinstance(result,TrashDirectory))
        self.assertEqual(Path('/mnt/disk/.Trash-999'), result.path)

class Method1VolumeTrashDirectoryTest(TestCase):
    def setUp(self):
        Path("sandbox").remove()
        Path("sandbox").mkdirs()
        
    @raises(TopDirWithoutStickyBit)
    def test_check_when_no_sticky_bit(self):
        # prepare
        import subprocess
        topdir = Path("sandbox").join("trash-dir")
        topdir.mkdirs()
        assert subprocess.call(["chmod", "-t", topdir.path]) == 0
        volume = Volume(Path("/mnt/disk"), True)
        instance = Method1VolumeTrashDirectory(topdir.join("123"), volume)
        
        instance.check()
        
    @raises(TopDirNotPresent)
    def test_check_when_no_dir(self):
        # prepare
        import subprocess
        topdir = Path("sandbox").join("trash-dir")
        topdir.touch()
        assert subprocess.call(["chmod", "+t", topdir.path]) == 0
        volume = Volume(Path("/mnt/disk"), True)
        instance = Method1VolumeTrashDirectory(topdir.join("123"), volume)
        
        instance.check()

    @raises(TopDirIsSymLink)
    def test_check_when_is_symlink(self):
        # prepare
        import subprocess
        topdir = Path("sandbox").join("trash-dir")
        topdir.mkdir()
        assert subprocess.call(["chmod", "+t", topdir.path]) == 0
        
        topdir_link = Path("sandbox/trash-dir-link")
        topdir_link.write_link("./trash-dir")
        volume = Volume(Path("/mnt/disk"), True)
        instance = Method1VolumeTrashDirectory(topdir_link.join("123"), volume)
        
        instance.check()
        
    def test_check_pass(self):
        # prepare
        import subprocess
        topdir = Path("sandbox").join("trash-dir")
        topdir.mkdirs()
        assert subprocess.call(["chmod", "+t", topdir.path]) == 0
        volume = Volume(Path("/mnt/disk"), True)
        instance = Method1VolumeTrashDirectory(topdir.join("123"), volume)
        
        instance.check() # should pass

Path("./sandbox").remove()
Path("./sandbox").mkdir()

