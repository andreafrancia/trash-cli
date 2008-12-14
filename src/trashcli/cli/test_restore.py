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

from . restore import RestoreCommand
from restore import *
from datetime import *
from exceptions import *
import os
import unittest
import pdb
from mock import Mock
from optparse import OptionParser
from ..libtrash import TrashedFile
from ..libtrash

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
    def test_execute_call_version(self):
        instance = RestoreCommand()
        instance.print_version = Mock()
        instance.execute(["--version"])
        instance.print_version.assert_called_with()
    
    def teste_execute_call_restore(self):
        instance = RestoreCommand()
        instance.execute("foo", "")
        pass
    
    def test_find_latest_trashed_file(self):
        list = []
        list.append(TrashedFile("pippo", TrashInfo