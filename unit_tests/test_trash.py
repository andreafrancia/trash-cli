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

from trashcli.trash import TrashDirectory
from trashcli.trash import TrashedFile
from trashcli.trash import TrashInfo
from trashcli.trash import VolumeTrashDirectory
from trashcli.trash import TimeUtils
from trashcli.trash import HomeTrashDirectory
from trashcli.trash import Path, mkdirs
from trashcli.trash import Volume
from trashcli.trash import TopDirIsSymLink
from trashcli.trash import TopDirNotPresent
from trashcli.trash import TopDirWithoutStickyBit
from trashcli.trash import Method1VolumeTrashDirectory

from integration_tests.files import require_empty_dir

from datetime import datetime
import os
from unittest import TestCase
from nose.tools import raises
from nose.tools import assert_equals

class TestTrashDirectory(TestCase) :

    def test_init(self) :
        path = Path("/mnt/disk/.Trash-123")
        volume = Volume(Path("/mnt/disk"), True);
        instance = TrashDirectory(path, volume)
        
        self.assertEquals(volume, instance.volume)
        self.assertEquals(path, instance.path)
        

    def test_trash(self) :
        #instance
        instance=VolumeTrashDirectory(
                        Path("sandbox/trash-directory"), 
                        Path("sandbox").volume)

        # test
        file_to_trash=Path("sandbox/dummy.txt")
        touch(file_to_trash)
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
        touch(Path("sandbox/foo/bar"))
        instance = trash_dir.trash(Path("sandbox/foo/bar"))
        Path("sandbox/foo").remove()
        instance.restore()
        assert Path("sandbox/foo/bar").exists() == True

class TestTimeUtils(TestCase) :
    def test_parse_iso8601(self) :
        expected=datetime(2008,9,8,12,00,11)
        result=TimeUtils.parse_iso8601("2008-09-08T12:00:11")
        self.assertEqual(expected,result)

class Method1VolumeTrashDirectoryTest(TestCase):
    def setUp(self):
        require_empty_dir('sandbox')
        
    @raises(TopDirWithoutStickyBit)
    def test_check_when_no_sticky_bit(self):
        # prepare
        import subprocess
        topdir = Path("sandbox").join("trash-dir")
        mkdirs(topdir)
        assert subprocess.call(["chmod", "-t", topdir.path]) == 0
        volume = Volume(Path("/mnt/disk"), True)
        instance = Method1VolumeTrashDirectory(topdir.join("123"), volume)
        
        instance.check()
        
    @raises(TopDirNotPresent)
    def test_check_when_no_dir(self):
        # prepare
        import subprocess
        topdir = Path("sandbox").join("trash-dir")
        touch(topdir)
        assert subprocess.call(["chmod", "+t", topdir.path]) == 0
        volume = Volume(Path("/mnt/disk"), True)
        instance = Method1VolumeTrashDirectory(topdir.join("123"), volume)
        
        instance.check()

    @raises(TopDirIsSymLink)
    def test_check_when_is_symlink(self):
        # prepare
        import subprocess
        topdir = Path("sandbox").join("trash-dir")
        mkdirs(topdir)
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
        mkdirs(topdir)
        assert subprocess.call(["chmod", "+t", topdir.path]) == 0
        volume = Volume(Path("/mnt/disk"), True)
        instance = Method1VolumeTrashDirectory(topdir.join("123"), volume)
        
        instance.check() # should pass

Path("./sandbox").remove()
Path("./sandbox").mkdir()
def touch(path):
    open(path, 'a+').close()
