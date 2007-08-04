#!/usr/bin/python

"""
Unit test for Volume.py
"""

__author__ = "Andrea Francia (andrea.francia@users.sourceforge.net)"
__copyright__ = "Copyright (c) 2007 Andrea Francia"
__license__ = "GPL"

from volume import *
from trashdirectory import *
import trashdirectory
import unittest
from trashinfo import *
import trashinfo
from datetime import *
from exceptions import *
import trashedfile

class TestVolume(unittest.TestCase) :
    def testListVolumes(self) : 
        volumes = volume.all()
        self.assertTrue(len(volumes) > 0)
        for v in volumes:
            self.assertTrue(isinstance(v, Volume))


class TestTrashDirectory(unittest.TestCase) :
    def testCreationFromVolume(self) :
        volume = Volume("/")
        td_list = trashdirectory.getVolumeTrashDirectories(volume)
        self.assertTrue(len(td_list) > 0)            
        for td in td_list :
            # is a trash direcory
            self.assertTrue(isinstance(td,TrashDirectory))
            # is in the volume
            self.assertTrue(td.getPath().startswith(volume.getPath()))

    def testBasePath(self) :
        os.environ['HOME'] = "/home/test"
        td = trashdirectory.getHomeTrashDirectory()
        self.assertEqual(td.getBasePath(),"/")

        td_list = trashdirectory.getVolumeTrashDirectories(Volume("/"))
        for td in td_list :
            self.assertEqual(td.getBasePath(), "/")
        
        
class TestTrashInfo(unittest.TestCase) :
    def testCreation(self) :
        data = """[Trash Info]
Path=home%2Fandrea%2Fprova.txt
DeletionDate=2007-07-23T23:45:07"""
        ti = trashinfo.parse(data)
        self.assertEqual(ti.getPath(), "home/andrea/prova.txt")
        self.assertTrue(isinstance(ti.getDeletionTime(),datetime))
        self.assertEqual(ti.getDeletionTime(), datetime(2007, 7, 23, 23, 45, 07))
        
    def testFailCreation(self) :
        data = "asdkjlfklajds"
        self.assertRaises(ValueError, trashinfo.parse, data)

class TestTrashedFile(unittest.TestCase) :
    def testCreation(self) :
        ti = trashinfo.TrashInfo()
        ti.path = "pippo"
        ti.deletionTime = datetime(2007, 7, 23, 23, 45, 07)
        td = trashdirectory.getHomeTrashDirectory()
        tf = trashedfile.TrashedFile(ti, td)
        self.assertEqual(tf.getPath(),"/pippo")
        self.assertEqual(ti.getDeletionTime(), tf.getDeletionTime())
        
    
if __name__ == "__main__":
    unittest.main()

                        
