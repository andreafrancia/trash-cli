#!/usr/bin/python
# libtrash/tests/__init__.py: Unit tests for libtrash.py classes.
#
# Copyright (C) 2007,2008 Andrea Francia Trivolzio(PV) Italy
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

__all__=["test_filesystem"]

from .trash import TrashDirectory
from .trash import TrashedFile
from .trash import TrashInfo
from .trash import VolumeTrashDirectory
from .trash import TimeUtils
from .trash import HomeTrashDirectory
from .filesystem import Path
from .filesystem import Volume

from datetime import *
from exceptions import *
import os
import unittest
import pdb
import sys


class TestTrashDirectory(unittest.TestCase) :
    def test_init(self) :
        path = Path("/mnt/disk/.Trash-123")
        volume = Volume(Path("/mnt/disk"), True);
        instance = TrashDirectory(path, volume)
        
        self.assertEquals(volume,instance.volume)
        self.assertEquals(path, instance.path)
        
    def testBasePath(self) :
        os.environ['HOME'] = "/home/test"
        td = TrashDirectory.getHomeTrashDirectory()
        self.assertEqual(Path("/"), td.volume)
    def test_trash(self) :
        #instance
        instance=TrashDirectory(
                        Path("sandbox/trash-directory"), 
                        Path("sandbox").volume)

        # test
        file_to_trash=Path("sandbox/dummy.txt")
        file_to_trash.touch()
        instance._path_for_trashinfo = lambda fileToTrash : Path("/dummy.txt")
        result = instance.trash(file_to_trash)
        self.assertTrue(isinstance(result,TrashedFile))
        self.assertEquals(Path("/dummy.txt"), result.path)
        self.assertTrue(result.getDeletionTime() is not None)

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
    def test_common_trash_dir(self) :
        # prepare
        TrashDirectory._getuid = staticmethod(lambda: 999)

        # execute
        result = TrashDirectory.common_trash_dir(Volume(Path("/mnt/disk")))        
        
        # check
        self.assert_(isinstance(result,TrashDirectory))
        self.assertEqual('/mnt/disk/.Trash/999', result.path.path)

    def test_getCommonTrashDirectory(self) :        
        #prepare
        TrashDirectory._getuid = staticmethod(lambda: 999)
        
        # invoke
        result = TrashDirectory.getUserTrashDirectory(Volume(Path("/mnt/disk")))
        
        # check
        self.assert_(isinstance(result,TrashDirectory))
        self.assertEqual(Path('/mnt/disk/.Trash-999'), result.path)
         
class TestTrashDirectory_persit_trash_info(unittest.TestCase) :
    def setUp(self):
        trashdirectory_base_dir = Path(os.path.realpath("./sandbox/testTrashDirectory"))
        trashdirectory_base_dir.remove()
        
        self.instance=TrashDirectory(trashdirectory_base_dir, Volume(Path("/")))
        
    def test_persist_trash_info_first_time(self):
        trash_info=TrashInfo(Path("dummy-path"), datetime(2007,01,01))

        result=self.instance.persist_trash_info(trash_info)

        self.assertTrue(isinstance(result, str))
        self.assertEquals('dummy-path', result)
        trash_info_file=self.instance.getTrashInfoFile(result)
        self.assertTrue(trash_info_file.exists())
        self.assertEquals("""[Trash Info]
Path=dummy-path
DeletionDate=2007-01-01T00:00:00
""", trash_info_file.read())
        
    def test_persist_trash_info_first_100_times(self):
        self.test_persist_trash_info_first_time()
        
        for i in range(1,100) :
            trash_info=TrashInfo(Path("dummy-path"), datetime(2007,01,01))
            
            result=self.instance.persist_trash_info(trash_info)
    
            self.assertTrue(isinstance(result, str))
            self.assertEquals('dummy-path'+"_" + str(i), result)
            trash_info_file=self.instance.getTrashInfoFile(result)
            self.assertTrue(trash_info_file.exists())
            self.assertEquals("""[Trash Info]
Path=dummy-path
DeletionDate=2007-01-01T00:00:00
""", trash_info_file.read())

    def test_persist_trash_info_other_times(self):
        self.test_persist_trash_info_first_100_times()
        
        for i in range(101,200) :
            trash_info=TrashInfo(Path("dummy-path"), datetime(2007,01,01))
            
            result=self.instance.persist_trash_info(trash_info)
    
            self.assertTrue(isinstance(result, str))
            self.assertTrue(result.startswith("dummy-path_"))
            trash_info_file=self.instance.getTrashInfoFile(result)            
            self.assertTrue(trash_info_file.exists())
            self.assertEquals("""[Trash Info]
Path=dummy-path
DeletionDate=2007-01-01T00:00:00
""", trash_info_file.read())


       
class TestHomeTrashDirectory(unittest.TestCase) :
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
                          
class TestVolumeTrashDirectory(unittest.TestCase) :
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
                    
class TestTrashInfo(unittest.TestCase) :
    def test_parse(self) :
        data = """[Trash Info]
Path=home%2Fandrea%2Fprova.txt
DeletionDate=2007-07-23T23:45:07"""
        result = TrashInfo.parse(data)
        self.assertEqual(result.path, "home/andrea/prova.txt")
        self.assert_(isinstance(result.getDeletionTime(),datetime))
        self.assertEqual(result.getDeletionTime(),
                         datetime(2007, 7, 23, 23, 45, 07))
        
    def test_init(self) :
        instance = TrashInfo(Path("path"), datetime(2007, 7, 23, 23, 45, 07))
        self.assertEquals("path", instance.path)
        self.assertEquals(datetime(2007, 7, 23, 23, 45, 07), instance.getDeletionTime())

    def test_init2(self) :
        instance = TrashInfo(Path("path"), datetime(2007, 7, 23, 23, 45, 07))
        self.assertEquals("path", instance.path)
        self.assertEquals(datetime(2007, 7, 23, 23, 45, 07), instance.getDeletionTime())
    
    def test_getDeletionTimeAsString(self) :
        instance = TrashInfo(Path("path"), datetime(2007, 7, 23, 23, 45, 07))
        self.assertEquals("2007-07-23T23:45:07", instance.getDeletionTimeAsString())
        

class TestTrashedFile(unittest.TestCase) :
    __dummy_datetime=datetime(2007, 7, 23, 23, 45, 07)
    
    def test_init(self) :
        os.environ['HOME']='/home/user'
        trash_directory = TrashDirectory.getHomeTrashDirectory()
        trashinfo = TrashInfo(Path("pippo"), datetime(2007, 7, 23, 23, 45, 07))

        instance = TrashedFile("dummy-id", trashinfo, trash_directory)
        
        self.assertEqual("dummy-id", instance.id)
        self.assertEqual(Path("/pippo"), instance.path)
        self.assertEqual(datetime(2007, 7, 23, 23, 45, 07), instance.getDeletionTime())
        self.assertEqual(trash_directory, instance.trash_directory)
        
    def test_original_location_when_absolute(self) :
        instance = TrashedFile(
            "dummy-id",
            TrashInfo(Path("/foo"), self.__dummy_datetime),
            TrashDirectory(Path("/mnt/volume/Trash/123"), Volume(Path("/mnt/volume"))))
        self.assertEqual(instance.original_location.path, "/foo")
        
    def test_original_location_when_relative(self):
        instance = TrashedFile(
            "dummy-id",
            TrashInfo(Path("foo"), self.__dummy_datetime),
            TrashDirectory(Path("/mnt/volume/Trash/123"), Volume(Path("/mnt/volume"))))
        self.assertEqual(instance.original_location.path, "/mnt/volume/foo")
            
class TestTimeUtils(unittest.TestCase) :
    def test_parse_iso8601(self) :
        expected=datetime(2008,9,8,12,00,11)
        result=TimeUtils.parse_iso8601("2008-09-08T12:00:11")
        self.assertEqual(expected,result)

        
Path("./sandbox").remove()
Path("./sandbox").mkdir()
