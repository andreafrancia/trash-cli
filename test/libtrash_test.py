#!/usr/bin/python
# test_libtrash.py: Unit tests for libtrash.py classes.
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

"""
Unit test for Volume.py
"""

__author__ = "Andrea Francia (andrea.francia@users.sourceforge.net)"
__copyright__ = "Copyright (c) 2007 Andrea Francia"
__license__ = "GPL"

import libtrash
from libtrash import *
from datetime import *
from exceptions import *
import os
import unittest

class TestFile(unittest.TestCase) :
    def test_constructor(self) :
        instance = File("dummy/path")
    
    def test_cmp(self) :
        self.assertNotEquals(File("."),File(os.path.realpath(".")))
        self.assertNotEquals(File("foo"),File("bar"))
        self.assertEquals(File("bar"),File("bar"))
        self.assertEquals(File("foo"),File("./foo"))
    
    def test_parent(self) :
        instance = File("dummy/path")
        self.assertEquals(File("dummy"), instance.parent)
    
    def test_creation(self) :
        path = os.path.abspath("adsljfkl");
        f = File(path);
        
    def test_basename(self) :
        f = File(os.path.join(os.sep, "dirname", "basename"))
        self.assertEqual(f.basename, "basename")

        f = File(os.path.join(os.sep, "dirname", "basename") + os.sep)
        self.assertEqual(f.basename, "basename")
    
    def test_realpath(self) :
        instance = File("dummy")
        self.assertEquals(os.path.realpath("dummy"), instance.realpath)

    def test_isabs_returns_true(self) :
        instance = File("/foo")
        self.assertEquals(True,instance.isabs())

    def test_isabs_returns_false(self) :
        instance = File("/foo")
        self.assertEquals(True,instance.isabs())

    def test_isabs_returns_on_windows(self) :
        instance = File("C:/foo")
        self.assertEquals(True,instance.isabs())

    def test_join_with_File_relative(self) :
        instance=File("/foo")
        result=instance.join(File("bar"))
        self.assertEquals(File("/foo/bar"),result)

    def test_join_with_File_absolute(self) :
        instance=File("/foo")
        try : 
            instance.join(File("/bar"))
            self.fail()
        except ValueError: 
            pass

    def test_join_with_str(self):
        instance=File("/foo")
        result=instance.join("bar")
        self.assertEquals(File("/foo/bar"),result)

    def test_list(self):
        instance=File("test-dir")
        instance.mkdir()
        instance.join("file1").touch()
        instance.join("file2").touch()
        instance.join("file3").touch()
        result=instance.list()
        self.assertEquals("<type 'generator'>", str(type(result)))
        # is much easier test the content of a list than a generator
        result_as_list=list(result)
        self.assertEquals(3, len(result_as_list))
        self.assertTrue(File("test-dir/file1") in result_as_list)
        self.assertTrue(File("test-dir/file1") in result_as_list)
        self.assertTrue(File("test-dir/file1") in result_as_list)

        # clean up
        instance.remove()

    def test_mkdir(self):
        instance=File("test-dir")
        instance.remove()
        self.assertFalse(instance.exists())
        instance.mkdir()
        self.assertTrue(instance.exists())
        self.assertTrue(instance.isdir())
        instance.remove() # clean up

    def test_mkdirs_with_default_mode(self):
        # prepare
        File("test-dir").remove()
        self.assertFalse(File("test-dir").exists())
        # perform
        instance=File("test-dir/sub-dir")
        instance.mkdirs()
        # test results
        self.assertTrue(instance.exists())
        self.assertTrue(instance.isdir())
        # clean up
        File("test-dir").remove()

    def test_mkdirs_with_default_mode(self):
        # prepare
        File("test-dir").remove()
        self.assertFalse(File("test-dir").exists())
        # perform
        instance=File("test-dir/sub-dir")
        instance.mkdirs()
        # test results
        self.assertTrue(instance.exists())
        self.assertTrue(instance.isdir())
        # clean up
        File("test-dir").remove()

    def test_touch(self):
        instance=File("test-file")
        instance.remove()
        self.assertFalse(instance.exists())
        instance.touch()
        self.assertTrue(instance.exists())
        self.assertFalse(instance.isdir())
        instance.remove() # clean up

class TestVolume(unittest.TestCase) :
    def test_all(self) :
        if sys.platform[:3] != "win":
            volumes = Volume.all()
            self.assert_(len(volumes) > 0)
            for v in volumes:
                self.assert_(isinstance(v, Volume))

    def testCmpVolumes(self) :
        v1 = Volume(File(os.sep))
        v2 = Volume(File(os.sep))

        self.assert_(v1 == v2)
        
    def test_getCommonTrashDirectory(self) :
        instance = Volume(File("/mnt/disk"))

        # invoke
        result = instance.getCommonTrashDirectory()
        
        # check
        self.assert_(isinstance(result,TrashDirectory))
        self.assertEqual('/mnt/disk/.Trash/999', result.path.path)

    def test_getCommonTrashDirectory(self) :        
        instance = Volume(File("/mnt/disk"), True)

        # invoke
        instance.getuid = lambda : 999
        result = instance.getUserTrashDirectory()
        
        # check
        self.assert_(isinstance(result,TrashDirectory))
        self.assertEqual(File('/mnt/disk/.Trash-999'), result.path)
        

class TestTrashDirectory(unittest.TestCase) :
    def test_init(self) :
        path = File("/mnt/disk/.Trash-123")
        volume = Volume(File("/mnt/disk"), True);
        instance = TrashDirectory(path, volume)
        
        self.assertEquals(volume,instance.volume)
        self.assertEquals(path, instance.path)
        
    def testBasePath(self) :
        os.environ['HOME'] = "/home/test"
        td = TrashDirectory.getHomeTrashDirectory()
        self.assertEqual(File("/"), td.volume)
        
    def testTrashInfoFileCreation(self) :
        trashdirectory_base_dir = File("./testTrashDirectory")
        trashdirectory_base_dir.remove()
        volume=Volume(File("/"))
        instance=TrashDirectory(trashdirectory_base_dir, volume)
        instance._path_for_trashinfo = lambda fileToBeTrashed : File("_path_for_trashinfo-result")
        
        fileToBeTrashed = File("/directory/filetobetrashed.ext")
        deletionTime = datetime(2007, 7, 23, 23, 45, 07)
        trashInfo = instance.createTrashInfo(fileToBeTrashed, deletionTime)

        # check that the result is a TrashInfo 
        self.assert_(isinstance(trashInfo, TrashInfo))

        # check that the trash info was placed in the "info" directory under
        # the TrashDirectory
        trashInfoFilePath = os.path.join(instance.getInfoPath(),
                                         trashInfo.getId() + ".trashinfo")

        self.assert_(os.path.exists(trashInfoFilePath))

        # check that the information recorded in the .trashinfo file are
        # the same we specified earlier
        trashInfo_as_readed = TrashInfo.parse(open(trashInfoFilePath).read())
        self.assertEqual(deletionTime, trashInfo_as_readed.getDeletionTime())
        self.assertEqual("_path_for_trashinfo-result", 
                         trashInfo_as_readed.path)

    def testCreateTrashInfo(self) :
        trashdirectory_base_dir = os.path.realpath("./testTrashDirectory")
        instance = TrashDirectory(trashdirectory_base_dir)
        for i in range(1,200) :
            deletion_date = datetime(2007,01,01)
            result=instance.createTrashInfo("dummy", deletion_date)
        

    def test_trash(self) :
        #instance
        instance=TrashDirectory(File("testTrashDirectory"), Volume(File("/")))

        # test
        filename = "dummy.txt"
        open(filename, "w").close()
        instance._path_for_trashinfo = lambda fileToTrash : File("/dummy.txt")
        result = instance.trash(File(filename))
        self.assertTrue(isinstance(result,TrashedFile))
        self.assertEquals(File("/dummy.txt"), result.path)
        self.assertTrue(result.getDeletionTime() is not None)

    def testCreateTrashInfo(self) : 
        instance = HomeTrashDirectory(File("./testTrashDir"))
        fileToBeTrashed=File("/home/user/test.txt")
        deletionTime=datetime(2000,1,1)
        
        result=instance.createTrashInfo(fileToBeTrashed, deletionTime)
        self.assertEquals(datetime(2000,1,1), result.getDeletionTime())
        
        # let test pass also on my windows developing machine
        self.assertEquals("/home/user/test.txt",result.path)

    def test_get_info_dir(self):
        instance=TrashDirectory(
            File("/mnt/disk/.Trash-123"),
            Volume(File("/mnt/disk"), True))
        self.assertEquals("/mnt/disk/.Trash-123/info", instance.info_dir)

    def test_get_files_dir(self):
        instance=TrashDirectory(
            File("/mnt/disk/.Trash-123"),
            Volume(File("/mnt/disk"), True))
        self.assertEquals("/mnt/disk/.Trash-123/files", instance.files_dir)
        
class TestHomeTrashDirectory(unittest.TestCase) :
    def test_path_for_trashinfo (self) : 
        instance = HomeTrashDirectory(File("/home/user/.local/share/Trash"))
        instance.volume = Volume(File("/"))

        # path for HomeTrashDirectory are always absolute
        fileToBeTrashed=File("/home/user/test.txt")
        result=instance._path_for_trashinfo(fileToBeTrashed)
        self.assertTrue(isinstance(result,File))
        self.assertEquals("/home/user/test.txt",result)
            
        #  ... even if the file is under /home/user/.local/share
        fileToBeTrashed=File("/home/user/.local/share/test.txt")
        result=instance._path_for_trashinfo(fileToBeTrashed)
        self.assertEquals(os.path.abspath("/home/user/.local/share/test.txt"),result)
        
class TestVolumeTrashDirectory(unittest.TestCase) :
    def test_init(self) :
        path = File("/mnt/disk/.Trash/123")
        volume = Volume(File("/mnt/disk"), True)
        instance = VolumeTrashDirectory(path, volume)
        self.assertEquals(path, instance.path)
        self.assertEquals(volume, instance.volume)
        
    def test_path_for_trashinfo (self) : 
        path = File("/mnt/disk/.Trash-123")
        volume = Volume(File("/mnt/volume"), True)
        instance = VolumeTrashDirectory(path, volume)

        # path for VolumeTrashDirectory are relative as possible
        fileToBeTrashed=File("/mnt/volume/directory/test.txt")
        result=instance._path_for_trashinfo(fileToBeTrashed)
        self.assertEquals("directory/test.txt",result)
            
        # path for VolumeTrashDirectory are relative as possible
        fileToBeTrashed=File("/mnt/other-volume/directory/test.txt")
        result=instance._path_for_trashinfo(fileToBeTrashed)
        self.assertEquals("/mnt/other-volume/directory/test.txt",result)
                    
class TestTrashInfo(unittest.TestCase) :
    def testParse(self) :
        data = """[Trash Info]
Path=home%2Fandrea%2Fprova.txt
DeletionDate=2007-07-23T23:45:07"""
        result = TrashInfo.parse(data)
        self.assertEqual(result.path, "home/andrea/prova.txt")
        self.assert_(isinstance(result.getDeletionTime(),datetime))
        self.assertEqual(result.getDeletionTime(),
                         datetime(2007, 7, 23, 23, 45, 07))
        
    def test_init(self) :
        instance = TrashInfo(File("path"), datetime(2007, 7, 23, 23, 45, 07))
        self.assertEquals("path", instance.path)
        self.assertEquals(datetime(2007, 7, 23, 23, 45, 07), instance.getDeletionTime())
        self.assertEquals(None, instance.getId())

    def test_init2(self) :
        instance = TrashInfo(File("path"), datetime(2007, 7, 23, 23, 45, 07), "id")
        self.assertEquals("path", instance.path)
        self.assertEquals(datetime(2007, 7, 23, 23, 45, 07), instance.getDeletionTime())
        self.assertEquals("id", instance.getId())
    
    def test_getDeletionTimeAsString(self) :
        instance = TrashInfo(File("path"), datetime(2007, 7, 23, 23, 45, 07))
        self.assertEquals("2007-07-23T23:45:07", instance.getDeletionTimeAsString())
        

class TestTrashedFile(unittest.TestCase) :
    __dummy_datetime=datetime(2007, 7, 23, 23, 45, 07)
    
    def test_init(self) :
        trash_directory = TrashDirectory.getHomeTrashDirectory()
        trashinfo = TrashInfo(File("pippo"), datetime(2007, 7, 23, 23, 45, 07))

        instance = TrashedFile(trashinfo, trash_directory)

        self.assertEqual(File("/pippo"), instance.path)
        self.assertEqual(datetime(2007, 7, 23, 23, 45, 07), instance.getDeletionTime())
        self.assertEqual(trash_directory, instance.trash_directory)
        
    def test_path_when_absolute(self) :
        instance = TrashedFile(
            TrashInfo(File("/foo"), self.__dummy_datetime),
            TrashDirectory(File("/mnt/volume/Trash/123"), Volume(File("/mnt/volume"))))
        self.assertEqual(instance.path, "/foo")
        
    def test_path_when_relative(self):
        instance = TrashedFile(
            TrashInfo(File("foo"), self.__dummy_datetime),
            TrashDirectory(File("/mnt/volume/Trash/123"), Volume(File("/mnt/volume"))))
        self.assertEqual(instance.path, "/mnt/volume/foo")
        
class TestTimeUtils(unittest.TestCase) :
    def test_parse_iso8601(self) :
        expected=datetime(2008,9,8,12,00,11)
        result=TimeUtils.parse_iso8601("2008-09-08T12:00:11")
        self.assertEqual(expected,result)

if __name__ == "__main__":
    unittest.main()
