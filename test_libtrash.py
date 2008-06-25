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

if dir(os).count('getuid') == 0 :
    def fake_getuid() :
        return 999;
    os.getuid = fake_getuid


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

class TestTrashDirectory(unittest.TestCase) :
    def testCreationFromVolume(self) :
        volume = Volume(os.sep) # main volume ("/"

        # test with /Trash/$uid
        td = volume.getCommonTrashDirectory()
        # is a trash direcory
        self.assert_(isinstance(td,TrashDirectory))
        # is in the volume
        self.assert_(td.getPath().startswith(volume.getPath()))

        # test with /Trash-$uid
        td = volume.getUserTrashDirectory()
        # is a trash direcory
        self.assert_(isinstance(td,TrashDirectory))
        # is in the volume
        self.assert_(td.getPath().startswith(volume.getPath()))


    def testBasePath(self) :
        os.environ['HOME'] = "/home/test"
        td = TrashDirectory.getHomeTrashDirectory()
        self.assertEqual(td.getBasePath(),os.path.abspath("/"))
        
    def testTrashInfoFileCreation(self) :
        trashdirectory_base_dir = os.path.realpath("./testTrashDirectory")
        td = TrashDirectory(trashdirectory_base_dir)
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
        self.assertEqual(fileToBeTrashed.getPath(),
                         trashInfo_as_readed.getPath())

    def testTrashingFile(self) :
        # create a empty file
        filename = "dummy.txt"
        open(filename, "w").close()

        # trash the file
        trashDirectory = TrashDirectory("testTrashDirectory")
        trashDirectory.trash(File(filename))

class TestTrashInfo(unittest.TestCase) :
    def testCreation(self) :
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
        tf = TrashedFile(ti, td)
        root = os.path.abspath(os.sep)
        self.assertEqual(tf.getPath(), os.path.join(root,"pippo"))
        self.assertEqual(ti.getDeletionTime(), tf.getDeletionTime())
        
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
    
