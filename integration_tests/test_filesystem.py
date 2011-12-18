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

from trashcli.trash import has_sticky_bit, mkdirs

from .files import require_empty_dir, having_file, set_sticky_bit
import os

class TestWithInSandbox:
    def test_mkdirs_with_default_mode(self):

        mkdirs("sandbox/test-dir/sub-dir")

        assert os.path.isdir("sandbox/test-dir/sub-dir")

    def test_has_sticky_bit_returns_true(self):

        having_file( "sandbox/sticky")
        run('chmod +t sandbox/sticky')

        assert has_sticky_bit('sandbox/sticky')
        
    def test_has_sticky_bit_returns_false(self):

        having_file( "sandbox/non-sticky")
        run('chmod -t sandbox/non-sticky')

        assert not has_sticky_bit("sandbox/non-sticky")

    def setUp(self):
        require_empty_dir('sandbox')

class Test_is_sticky_dir:

    def test_dir_non_sticky(self):
        mkdirs('sandbox/dir'); assert not is_sticky_dir('sandbox/dir')

    def test_dir_sticky(self):
        mkdirs('sandbox/dir'); set_sticky_bit('sandbox/dir')
        assert is_sticky_dir('sandbox/dir')

    def test_non_dir_but_sticky(self):
        having_file('sandbox/dir');
        set_sticky_bit('sandbox/dir')
        assert not is_sticky_dir('sandbox/dir')

    def setUp(self):
        require_empty_dir('sandbox')

def is_sticky_dir(path):
    import os
    return os.path.isdir(path) and has_sticky_bit(path)

def run(command):
    import subprocess
    assert subprocess.call(command.split()) == 0

