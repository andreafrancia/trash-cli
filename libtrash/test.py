#!/usr/bin/python

"""
Unit test for Volume.py
"""

__author__ = "Andrea Francia (andrea.francia@users.sourceforge.net)"
__copyright__ = "Copyright (c) 2007 Andrea Francia"
__license__ = "GPL"

from volume import Volume
from trash_directory import TrashDirectory
from trash_info import TrashInfo
from trashed_file import TrashedFile
from file import File

import trash_directory
import unittest
import trash_info
import trashed_file
import volume

from datetime import *
from exceptions import *
import os

if dir(os).count('getuid') == 0 :
    def fake_getuid() :
        return 999;
    os.getuid = fake_getuid


class TestVolume(unittest.TestCase) :
    def testListVolumes(self) : 
        volumes = volume.all()
        self.assertTrue(len(volumes) > 0)
        for v in volumes:
            self.assertTrue(isinstance(v, Volume))

    def testCmpVolumes(self) :
        v1 = Volume(os.sep)
        v2 = Volume(os.sep)

        self.assertTrue(v1 == v2)

class TestTrashDirectory(unittest.TestCase) :
    def testCreationFromVolume(self) :
        volume = Volume(os.sep) # main volume ("/"
        td_list = trash_directory.getVolumeTrashDirectories(volume)
        self.assertTrue(len(td_list) > 0)            
        for td in td_list :
            # is a trash direcory
            self.assertTrue(isinstance(td,TrashDirectory))
            # is in the volume
            self.assertTrue(td.getPath().startswith(volume.getPath()))


    def testBasePath(self) :
        os.environ['HOME'] = "/home/test"
        td = trash_directory.getHomeTrashDirectory()
        self.assertEqual(td.getBasePath(),os.path.abspath("/"))
        
        root = os.path.abspath(os.sep)
        td_list = trash_directory.getVolumeTrashDirectories(Volume(root))
        for td in td_list :
            self.assertEqual(td.getBasePath(), root)

    def testTrashInfoFileCreation(self) :
        trashdirectory_base_dir = os.path.realpath("./testTrashDirectory")
        td = TrashDirectory(trashdirectory_base_dir)
        fileToBeTrashed = File("/directory/filetobetrashed.ext")
        deletionTime = datetime(2007, 7, 23, 23, 45, 07)
        trashInfo = td.createTrashInfo(fileToBeTrashed, deletionTime)

        # check that the result is a TrashInfo 
        self.assertTrue(isinstance(trashInfo, TrashInfo))

        # check that the trash info was placed in the "info" directory under
        # the TrashDirectory
        trashInfoFilePath = os.path.join(td.getInfoPath(),
                                         trashInfo.getId() + ".trashinfo")

        self.assertTrue(os.path.exists(trashInfoFilePath))

        # check that the information recorded in the .trashinfo file are
        # the same we specified earlier
        trashInfo_as_readed = TrashInfo()
        trashInfo_as_readed.parse(open(trashInfoFilePath).read())
        self.assertEqual(deletionTime, trashInfo_as_readed.getDeletionTime())
        self.assertEqual(fileToBeTrashed.getPath(), trashInfo_as_readed.getPath())

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
        self.assertTrue(isinstance(ti.getDeletionTime(),datetime))
        self.assertEqual(ti.getDeletionTime(), datetime(2007, 7, 23, 23, 45, 07))
        
    def testFailCreation(self) :
        data = "asdkjlfklajds"
        ti = TrashInfo()
        self.assertRaises(ValueError, ti.parse, data)

class TestTrashedFile(unittest.TestCase) :
    def testCreation(self) :
        ti = TrashInfo()
        ti.path = "pippo"
        ti.deletionTime = datetime(2007, 7, 23, 23, 45, 07)
        td = trash_directory.getHomeTrashDirectory()
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

if __name__ == "__main__":
    unittest.main()
    
