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
from trashcli.trash import HomeTrashDirectory
from trashcli.filesystem import Path
from trashcli.filesystem import Volume

from trashcli.cli.restore import RestoreCommand
from trashcli.cli.restore import Restorer

class RestorerTest(unittest.TestCase):

    def test_restore_latest(self):
        class TrashedFileMock:
            def __init__(self, path, deletion_date, 
                         is_restore_call_expected=False):
                self.path = path
                self.deletion_date = deletion_date
                self.is_restore_call_expected = is_restore_call_expected
                self.restore_call_count = 0
                
            def restore(self):
                assert self.is_restore_call_expected
                self.restore_call_count+=1
            
        a_foo      = TrashedFileMock(Path('/foo'), datetime(2009,01,01))
        latest_foo = TrashedFileMock(Path('/foo'), datetime(2010,01,01), True)
        a_bar      = TrashedFileMock(Path('/bar'), datetime(2010,01,01))
        
        class TrashCanMock:
            def trashed_files(self):
                yield a_foo
                yield latest_foo
                yield a_bar 

                
        trashcan = TrashCanMock()
        instance = Restorer(trashcan)
        instance.restore_latest(Path('/foo'))
        
        assert latest_foo.restore_call_count == 1

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

        assert Restorer.last_trashed(before, after) is after
        assert Restorer.last_trashed(after, before) is after
    
        sametime1 = TrashedFile('foo', 
                                TrashInfo("foo", datetime(2009,01,01,01,01,01)),
                                trash_dir)
        sametime2 = TrashedFile('foo', 
                                TrashInfo("foo", datetime(2009,01,01,01,01,01)),
                                trash_dir)
        
        assert Restorer.last_trashed(sametime1, sametime2) is sametime1

    def test_both(self):
        def is_greater_than_1(elem):
            return elem > 1
        
        def is_lower_than_3(elem):
            return elem < 3
        
        def is_odd(elem):
            return elem % 2 == 1
        
        result1 = Restorer.both(is_greater_than_1, is_lower_than_3)
        result2 = Restorer.both(is_greater_than_1, is_odd)
        
        assert result1(1) == False
        assert result1(2) == True
        assert result1(3) == False
        assert result1(4) == False
    
        assert result2(1) == False
        assert result2(2) == False
        assert result2(3) == True
        assert result2(4) == False
    
