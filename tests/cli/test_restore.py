#!/usr/bin/python
# tests/cli/test_restore.py: Unit tests for trashcli.cli.restore classes.
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

"""
test module for the trashcli.cli.restore module
"""

from __future__ import absolute_import

__author__ = "Andrea Francia (andrea.francia@users.sourceforge.net)"
__copyright__ = "Copyright (c) 2007 Andrea Francia"
__license__ = "GPL"

from datetime import datetime
import os
import unittest
from unittest import TestCase
import pdb
from mock import Mock

from optparse import OptionParser
from trashcli.trash import TrashedFile
from trashcli.trash import TrashInfo
from trashcli.trash import TrashDirectory
from trashcli.trash import HomeTrashDirectory
from trashcli.cli.restore import TrashNotFoundError
from trashcli.filesystem import Path
from trashcli.filesystem import Volume
import trashcli.cli.restore
from trashcli.cli.restore import RestoreCommandLine
from trashcli.cli.restore import Restorer
from trashcli.cli.restore import find_latest
from trashcli.cli.restore import last_trashed

from nose.tools import assert_equals
from nose.tools import raises

class TrashedFileMock(object):
    def __init__(self, path, deletion_date):
        self.path = path
        self.deletion_date = deletion_date

    def __repr__(self):
        return "TrashedFileMock('%s','%s')" % (self.path, 
                                               self.deletion_date)

class FindLatestTest(TestCase):
    def test_find_latest(self):
        a_foo      = TrashedFileMock(Path('/foo'), datetime(2009, 01, 01))
        latest_foo = TrashedFileMock(Path('/foo'), datetime(2010, 01, 01))
        a_bar      = TrashedFileMock(Path('/bar'), datetime(2010, 01, 01))
        
        class TrashCanMock:
            def trashed_files(self):
                yield a_foo
                yield latest_foo
                yield a_bar 
        trashcan = TrashCanMock()
        
        # execute
        result = find_latest(trashcan, Path('/foo'))
        
        # test
        assert_equals(latest_foo, result)
    
    @raises(TrashNotFoundError)
    def test_find_latest_raises_TrashNotFoundError(self):
        class TrashCanMock:
            def trashed_files(self):
                yield TrashedFileMock(Path('/foo'), datetime(2009, 01, 01))
                yield TrashedFileMock(Path('/foo'), datetime(2010, 01, 01))
                yield TrashedFileMock(Path('/bar'), datetime(2010, 01, 01)) 
        trashcan = TrashCanMock()
        
        # execute
        find_latest(trashcan, Path('/goo'))
        
class LastTrashedTest(TestCase):
    def test_last_trashed(self):
        """
        Test that last_deleted returns the last trashed file.
        """
        trash_dir = TrashDirectory(Path('/.Trash/'), Volume(Path('/')))

        before = TrashedFile('foo', 
                             TrashInfo("foo", 
                                       datetime(2009, 01, 01, 01, 01, 01)),
                             trash_dir)
        after = TrashedFile('foo', 
                            TrashInfo("foo", 
                                      datetime(2009, 01, 01, 01, 01, 02)), 
                            trash_dir)

        assert last_trashed(before, after) is after
        assert last_trashed(after, before) is after
    
        sametime1 = TrashedFile('foo', 
                                TrashInfo("foo", datetime(2009, 01, 01, 
                                                          01, 01, 01)),
                                trash_dir)
        sametime2 = TrashedFile('foo', 
                                TrashInfo("foo", datetime(2009,01,01,
                                                          01,01,01)),
                                trash_dir)
        
        assert last_trashed(sametime1, sametime2) is sametime1
    
class RestorerTest(TestCase):
    def test_restore_latest_calls_find_latest_and_restore(self):
        # prepare
        latest = Mock()
        trashcan = Mock()
        find_latest = Mock(return_value=latest)
        
        instance = Restorer(trashcan, find_latest)
        # execute 
        instance.restore_latest(Path('/foo'))
        
        # check
        assert_equals(1, find_latest.call_count)
        find_latest.assert_called_with(trashcan, Path('/foo'))
        
        assert_equals(1, latest.restore.call_count)
        latest.restore.assert_called_with((None))

class RestoreCommandLineTest(TestCase):
    def test_call_restore_without_dest(self):
        restorer = Mock()
        instance = RestoreCommandLine(restorer)
        instance.execute(['/path-to-restore'])
        assert restorer.restore_latest.call_count == 1
        print restorer.restore_latest.call_args
        restorer.restore_latest.assert_called_with(
            Path('/path-to-restore'))
    
    def test_call_restore_with_dest(self):
        restorer = Mock()
        instance = RestoreCommandLine(restorer)
        instance.execute(['/path-to-restore', 'dest'])
        assert restorer.restore_latest.call_count == 1
        restorer.restore_latest.assert_called_with(
            Path('/path-to-restore'), Path('dest'))
    
