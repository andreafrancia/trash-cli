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

__author__="Andrea Francia (andrea.francia@users.sourceforge.net)"
__copyright__="Copyright (c) 2007 Andrea Francia"
__license__="GPL"

from datetime import *
from exceptions import *
import os
import unittest
import pdb
from mock import Mock
from optparse import OptionParser
from trashcli.trash import TrashedFile
from trashcli.trash import TrashInfo
from trashcli.trash import TrashInfo
from trashcli.trash import TrashDirectory
from trashcli.filesystem import Path
from trashcli.filesystem import Volume

from trashcli.cli.restore import RestoreCommand
from trashcli.cli.restore import create_option_parser
from trashcli.cli.restore import last_trashed
from trashcli.cli.restore import both


class TestRestoreParser(unittest.TestCase) :
    def test_version_option(self) :
        instance=create_option_parser()
        (option,args)=instance.parse_args(["--version"])
        assert option.version == True
        
    def test_help_option(self) :
        instance=create_option_parser()
        instance.exit = Mock()
        (option,args)=instance.parse_args(["--help"])
        assert instance.exit.called == True
        instance.exit.assert_called_with()
        
    def test_simple_usage(self):
        instance=create_option_parser()
        (option,args)=instance.parse_args(["file1", "file2", "file3"])
        assert args == ["file1", "file2", "file3"]
        
class TestRestoreCommand(unittest.TestCase):
    def __ignore_test_execute_call_version(self):
        instance = RestoreCommand()
        instance.print_version = Mock()
        instance.execute(["--version"])
        assert instance.print_version.called  == True
        instance.print_version.assert_called_with()
    
    
    def test_extract_return_only_matching_elements(self):
        alist = [1,2,3,4,5,6,7]
        def isodd(elem):
            return elem % 2 == 1
        assert [1,3,5,7] == list(filter(isodd,alist))
    
    def test_extract_TrashedFile(self):
        trash_dir = TrashDirectory(Path('/.Trash/'), Volume(Path('/')))
        
        alist=[TrashedFile('foo', 
                           TrashInfo(Path('foo'), datetime(2009,01,01)),
                           trash_dir),
               TrashedFile('foo_1',
                           TrashInfo(Path('foo'), datetime(2009,01,01)),
                           trash_dir),
               TrashedFile('bar',
                           TrashInfo(Path('bar'), datetime(2009,01,01)),
                           trash_dir)]
        
        def is_named_foo(item):
            return "foo" in str(item.path)
        
        result = list(filter(is_named_foo,alist))
        assert len(result) == 2
        assert result[0].id == 'foo'
        assert result[1].id == 'foo_1'

    def test_last_trashed(self):
        """
        Test that last_deleted returns the last trashed file.
        """
        trash_dir = TrashDirectory(Path('/.Trash/'), Volume(Path('/')))

        before = TrashedFile('foo', 
                             TrashInfo("foo", datetime(2009,01,01,01,01,01)), 
                             trash_dir)
        after = TrashedFile('foo', 
                            TrashInfo("foo", datetime(2009,01,01,01,01,02)), 
                            trash_dir)

        assert last_trashed(before, after) is after
        assert last_trashed(after, before) is after
    
        sametime1 = TrashedFile('foo', 
                                TrashInfo("foo", datetime(2009,01,01,01,01,01)),
                                trash_dir)
        sametime2 = TrashedFile('foo', 
                                TrashInfo("foo", datetime(2009,01,01,01,01,01)),
                                trash_dir)
        
        assert last_trashed(sametime1, sametime2) is sametime1

    def test_both(self):
        def is_greater_than_1(elem):
            return elem > 1
        
        def is_lower_than_3(elem):
            return elem < 3
        
        def is_odd(elem):
            return elem % 2 == 1
        
        result1 = both(is_greater_than_1, is_lower_than_3)
        result2 = both(is_greater_than_1, is_odd)
        
        assert result1(1) == False
        assert result1(2) == True
        assert result1(3) == False
        assert result1(4) == False
    
        assert result2(1) == False
        assert result2(2) == False
        assert result2(3) == True
        assert result2(4) == False
    
