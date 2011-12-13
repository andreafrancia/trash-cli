#!/usr/bin/python
# tests/test_filesystem.py: Unit tests for trashcli.filesystem module.
#
# Copyright (C) 2008-2009 Andrea Francia Trivolzio(PV) Italy
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

import unittest
from trashcli.trash import Volume
from trashcli.trash import Path, has_sticky_bit, mkdirs
import sys
import os
import subprocess
from nose.tools import assert_equals
from integration_tests.files import require_empty_dir

class TestVolume(unittest.TestCase) :
    def test_all(self) :

	volumes = Volume.all()
	self.assert_(len(list(volumes)) > 0)
	for v in volumes:
	    self.assert_(isinstance(v, Volume))

    def testCmpVolumes(self) :
        v1 = Volume(Path(os.sep))
        v2 = Volume(Path(os.sep))

        self.assert_(v1 == v2)

def _is_mac_os():
    return sys.platform == 'darwin'

def _is_cygwin():
    return sys.platform == 'cygwin' 


class TestPath(unittest.TestCase) :
    def test_constructor(self) :
        Path("dummy/path")
    
    def test_eq(self) :
        self.assertNotEquals(Path("."),Path(os.path.realpath(".")))
        self.assertNotEquals(Path("foo"),Path("bar"))
        self.assertEquals(Path("bar"),Path("bar"))
        self.assertEquals(Path("foo"),Path("./foo").norm())
        
        list1=(Path('bar'), Path('bur'))
        list2=(Path('bar'), Path('bur'))
        list3=(Path('foo'), Path('bur'))
        
        assert list1 == list2
        assert list1 != list3
        
    def test_parent(self) :
        instance = Path("dummy/path")
        self.assertEquals(Path("dummy"), instance.parent)
    
    def test_join_with_File_relative(self) :
        instance=Path("/foo")
        result=instance.join(Path("bar"))
        self.assertEquals(Path("/foo/bar"),result)

    def test_join_with_File_absolute(self) :
        instance=Path("/foo")
        try : 
            instance.join(Path("/bar"))
            self.fail()
        except ValueError: 
            pass

    def test_join_with_str(self):
        instance=Path("/foo")
        result=instance.join("bar")
        self.assertEquals(Path("/foo/bar"),result)

    def test_mkdir(self):
        require_empty_dir('sandbox')
        instance=Path("sandbox/test-dir")
        instance.remove()
        self.assertFalse(instance.exists())
        instance.mkdir()
        self.assertTrue(instance.exists())
        self.assertTrue(instance.isdir())
        instance.remove() # clean up

    def test_mkdirs_with_default_mode(self):
        # prepare
        Path("sandbox/test-dir").remove()
        self.assertFalse(Path("sandbox/test-dir").exists())
        # perform
        instance=Path("sandbox/test-dir/sub-dir")
        mkdirs(instance)
        # test results
        self.assertTrue(instance.exists())
        self.assertTrue(instance.isdir())
        # clean up
        Path("sandbox/test-dir").remove()

    def test_touch(self):
        instance=Path("sandbox/test-file")
        instance.remove()
        self.assertFalse(instance.exists())
        touch(instance)
        self.assertTrue(instance.exists())
        self.assertFalse(instance.isdir())
        instance.remove() # clean up
    
    def test_has_sticky_bit_returns_true(self):
        require_empty_dir('sandbox')
        sticky=Path("sandbox").join("sticky")
        touch(sticky)
        assert subprocess.call(["chmod", "+t", "sandbox/sticky"]) == 0
        assert has_sticky_bit(sticky)
        
    def test_has_sticky_bit_returns_false(self):
        require_empty_dir('sandbox')
        non_sticky=Path("sandbox").join("non-sticky")
        touch(non_sticky)
        assert subprocess.call(["chmod", "-t", "sandbox/non-sticky"]) == 0
        assert not has_sticky_bit(non_sticky)


    def test_type_descrition_for_directories(self):
        require_empty_dir('sandbox')
        
        assert_equals("directory", Path(".").type_description())
        assert_equals("directory", Path("..").type_description())
        assert_equals("directory", Path("sandbox").type_description())
        
    def test_name_for_regular_files(self):
        require_empty_dir('sandbox')
        Path("sandbox").join("non-empty").write_file("content")
        touch('sandbox/empty')
        
        assert_equals("regular file", Path("sandbox/non-empty").type_description())
        assert_equals("regular empty file", Path("sandbox/empty").type_description())
                
    def test_name_for_symbolic_links(self):
        require_empty_dir('sandbox')
        Path("sandbox").join("symlink").write_link('somewhere')
        
        assert_equals("symbolic link", Path("sandbox/symlink").type_description())

    def test_name_for_dot_directories(self):
        require_empty_dir('sandbox')

        assert_equals("`.' directory", Path("sandbox/.").type_description())
        assert_equals("`..' directory", Path("sandbox/..").type_description())
        
        assert_equals("`.' directory", Path("./.").type_description())
        assert_equals("`..' directory", Path("./..").type_description())

def touch(path):
    open(path,'w').close()
