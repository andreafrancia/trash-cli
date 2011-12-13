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

from nose.tools import assert_equals

from trashcli.trash import has_sticky_bit, mkdirs, describe, write_file
from integration_tests.files import require_empty_dir
clean_up=require_empty_dir

import os
import subprocess

class TestPath:

    def test_mkdirs_with_default_mode(self):
        require_empty_dir('sandbox')
        mkdirs("sandbox/test-dir/sub-dir")
        assert os.path.isdir("sandbox/test-dir/sub-dir")
        clean_up('sandbox')

    def test_touch(self):
        require_empty_dir('sandbox')
        touch('sandbox/new-file')
        assert os.path.isfile('sandbox/new-file')
        clean_up('sandbox')
    
    def test_has_sticky_bit_returns_true(self):
        require_empty_dir('sandbox')
        sticky="sandbox/sticky"
        touch(sticky)
        assert subprocess.call(["chmod", "+t", "sandbox/sticky"]) == 0
        assert has_sticky_bit(sticky)
        
    def test_has_sticky_bit_returns_false(self):
        require_empty_dir('sandbox')
        non_sticky="sandbox/non-sticky"
        touch(non_sticky)
        assert subprocess.call(["chmod", "-t", "sandbox/non-sticky"]) == 0
        assert not has_sticky_bit(non_sticky)

class TestDescritions:
    def setUp(self):
        require_empty_dir('sandbox')

    def test_type_descrition_for_directories(self):
        
        assert_equals("directory", describe('.'))
        assert_equals("directory", describe(".."))
        assert_equals("directory", describe("sandbox"))
        
    def test_name_for_regular_files(self):
        write_file("sandbox/non-empty", "contents")
        touch('sandbox/empty')
        
        assert_equals("regular file", describe("sandbox/non-empty"))
        assert_equals("regular empty file", describe("sandbox/empty"))
                
    def test_name_for_symbolic_links(self):
        os.symlink('somewhere', "sandbox/symlink")
        
        assert_equals("symbolic link", describe("sandbox/symlink"))

    def test_name_for_dot_directories(self):

        assert_equals("`.' directory",  describe("sandbox/."))
        assert_equals("`..' directory", describe("sandbox/.."))
        assert_equals("`.' directory",  describe("./."))
        assert_equals("`..' directory", describe("./.."))

def touch(path):
    open(path,'w').close()
