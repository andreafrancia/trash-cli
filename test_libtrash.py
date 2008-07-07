#!/usr/bin/python

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

class TestVolume(unittest.TestCase) :
    def testListVolumes(self) : 
        volumes = Volume.all()
        self.assert_(len(volumes) > 0)
        for v in volumes:
            self.assert_(isinstance(v, Volume))

    def testCmpVolumes(self) :
        v1 = Volume(os.sep)
        v2 = Volume(os.sep)

        self.assert_(v1 == v2)
        
    def test_getCommonTrashDirectory(self) :
        instance = Volume("/mnt/disk")

        # invoke
        result = instance.getCommonTrashDirectory()
        
        # check
        self.assert_(isinstance(result,TrashDirectory))
        self.assertEqual('/mnt/disk/.Trash/999', result.path.path)

    def test_getCommonTrashDirectory(self) :        
        instance = Volume("/mnt/disk", True)

        # invoke
        instance.getuid = lambda : 999
        result = instance.getUserTrashDirectory()
        
        # check
        self.assert_(isinstance(result,TrashDirectory))
        self.assertEqual(os.path.abspath('/mnt/disk/.Trash-999'), result.path.path)
        

class TestTrashDirectory(unittest.TestCase) :
    def test_init(self) :
        path = File("/mnt/disk/.Trash-123")
        volume = Volume("/mnt/disk", True);
        instance = TrashDirectory(path, volume)
        
        self.assertEquals(volume,instance.volume)
        self.assertEquals(path, instance.path)
        
    def testBasePath(self) :
        os.environ['HOME'] = "/home/test"
        td = TrashDirectory.getHomeTrashDirectory()
        self.assertEqual(td.getBasePath(),os.path.abspath("/"))
        
    def testTrashInfoFileCreation(self) :
        trashdirectory_base_dir = File(os.path.realpath("./testTrashDirectory"))
        volume=File("/")
        td = TrashDirectory(trashdirectory_base_dir, volume)
        td._path_for_trashinfo = lambda fileToBeTrashed : "_path_for_trashinfo-result"
        
        fileToBeTrashed = File("/directory/filetobetrashed.ext")
        deletionTime = datetime(2007, 7, 23, 23, 45, 07)
        trashInfo = td.createTrashInfo(fileToBeTrashed, deletionTime)

        # check that the result is a TrashInfo 
        self.assert_(isinstance(trashInfo, TrashInfo))

        # check that the trash info was placed in the "info" directory under
        # the TrashDirectory
        trashInfoFilePath = os.path.join(td.getInfoPath(),
                                         trashInfo.getId() + ".trashinfo")

        self.assert_(os.path.exists(trashInfoFilePath))

        # check that the information recorded in the .trashinfo file are
        # the same we specified earlier
        trashInfo_as_readed = TrashInfo()
        trashInfo_as_readed.parse(open(trashInfoFilePath).read())
        self.assertEqual(deletionTime, trashInfo_as_readed.getDeletionTime())
        self.assertEqual("_path_for_trashinfo-result", 
                         trashInfo_as_readed.getPath())

    def testCreateTrashInfo(self) :
        trashdirectory_base_dir = os.path.realpath("./testTrashDirectory")
        td = TrashDirectory(trashdirectory_base_dir)
        

    def testTrashingFile(self) :
        # create a empty file
        filename = "dummy.txt"
        open(filename, "w").close()

        # trash the file
        trashDirectory = TrashDirectory(File("testTrashDirectory"), File("/"))
        trashDirectory._path_for_trashinfo = lambda fileToBeTrashed : "_path_for_trashinfo-result"
        trashDirectory.trash(File(filename))

    def testCreateTrashInfo(self) : 
        instance = HomeTrashDirectory(File("/home/user/.local/share/Trash"))
        fileToBeTrashed=File("/home/user/test.txt")
        deletionTime=datetime(2000,1,1)
        
        result=instance.createTrashInfo(fileToBeTrashed, deletionTime)
        self.assertEquals(datetime(2000,1,1), result.deletionTime)
        
        # let test pass also on my windows developing machine
        if(sys.platform!="win32") :
            self.assertEquals("/home/user/test.txt",result.getPath())
        else:
            self.assertEquals("C:\\home\\user\\test.txt",result.getPath())
            
        
class TestHomeTrashDirectory(unittest.TestCase) :
    def test_path_for_trashinfo (self) : 
        instance = HomeTrashDirectory(File("/home/user/.local/share/Trash"))
        instance.volume = Volume("/")

        # path for HomeTrashDirectory are always absolute
        fileToBeTrashed=File("/home/user/test.txt")
        result=instance._path_for_trashinfo(fileToBeTrashed)
        self.assertEquals(os.path.abspath("/home/user/test.txt"),result)
            
        #  ... even if the file is under /home/user/.local/share
        fileToBeTrashed=File("/home/user/.local/share/test.txt")
        result=instance._path_for_trashinfo(fileToBeTrashed)
        self.assertEquals(os.path.abspath("/home/user/.local/share/test.txt"),result)

        
class TestVolumeTrashDirectory(unittest.TestCase) :
    def test_init(self) :
        path = File("/mnt/disk/.Trash/123")
        volume = Volume("/mnt/disk", True)
        instance = VolumeTrashDirectory(path, volume)
        self.assertEquals(path, instance.path)
        self.assertEquals(volume, instance.volume)
        
    def test_path_for_trashinfo (self) : 
        path = File("/mnt/disk/.Trash-123")
        volume = Volume("/mnt/volume", True)
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
        ti = TrashInfo()
        data = """[Trash Info]
Path=home%2Fandrea%2Fprova.txt
DeletionDate=2007-07-23T23:45:07"""
        ti.parse(data)
        self.assertEqual(ti.getPath(), "home/andrea/prova.txt")
        self.assert_(isinstance(ti.getDeletionTime(),datetime))
        self.assertEqual(ti.getDeletionTime(),
                         datetime(2007, 7, 23, 23, 45, 07))
        
    def testFailCreation(self) :
        data = "asdkjlfklajds"
        ti = TrashInfo()
        self.assertRaises(ValueError, ti.parse, data)

class TestTrashedFile(unittest.TestCase) :
    def testCreation(self) :
        ti = TrashInfo()
        ti.path = "pippo"
        ti.deletionTime = datetime(2007, 7, 23, 23, 45, 07)
        td = TrashDirectory.getHomeTrashDirectory()
        instance = TrashedFile(ti, td)
        root = os.path.abspath(os.sep)
        self.assertEqual(instance.getPath(), os.path.join(root,"pippo"))
        self.assertEqual(ti.getDeletionTime(), instance.getDeletionTime())
        
class TestFile(unittest.TestCase) :
    def test_creation(self) :
        path = os.path.abspath("adsljfkl");
        f = File(path);
        
    def test_getBasename(self) :
        f = File(os.path.join(os.sep, "dirname", "basename"))
        self.assertEqual(f.getBasename(), "basename")

        f = File(os.path.join(os.sep, "dirname", "basename") + os.sep)
        self.assertEqual(f.getBasename(), "basename")

class TestTimeUtils(unittest.TestCase) :
    def test_parse_iso8601(self) :
        expected=datetime(2008,9,8,12,00,11)
        result=TimeUtils.parse_iso8601("2008-09-08T12:00:11")
        self.assertEqual(expected,result)

if __name__ == "__main__":
    unittest.main()
