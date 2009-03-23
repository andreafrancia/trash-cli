#!/usr/bin/python
# tests/command_tests/test_put.py: Tests for the trash-put command.
#
# Copyright (C) 2009 Andrea Francia Trivolzio(PV) Italy
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

from unittest import TestCase
from trashcli.filesystem import Path
from trashcli.trash import HomeTrashDirectory
from nose.tools import assert_equals
from nose.tools import assert_not_equals
from nose.tools import assert_true
from nose.tools import assert_false
from nose.tools import raises
from nose import SkipTest
from cmd import Command

put_cmd='trash-put'

class Sandbox():
    """
    A sandbox where executing commands under tests
    """
    def __init__(self):
        self.path=Path("./sandbox")
        self.path.remove()
        self.path.mkdirs()
        self.env = {'HOME':'./sandbox/home'}
        self.trashdir = HomeTrashDirectory(
            Path('./sandbox/home/.local/share/Trash'))

    def create_file(self, path, content=None):
        """
        Create a file in sandbox with content
        """
        file=self.path.join(path)
        file.touch()
        if content!=None :
            file.write_file(content)
            
        return file

    def trash(self, path):
        """
        Trash the file in the trash dir at sandbox/home/.local/share/Trash
        """
        result = self.trashdir.trash(path)
        
        # sanity check 
        assert not path.exists()
        return result
 
    def execute(self, *cmdline) :
        """
        Create a command with the current enviroment (self.env)
        """
        return Command(cmdline, self.env, self.path).run()

class Test(TestCase):
   
    def setUp(self):
        self.sandbox = Sandbox()
    
    # Rule of Silence: When a program has nothing surprising to say, it should say nothing.
    # See also:
    #  - issue #32 
    #  - http://www.catb.org/~esr/writings/taouu/taouu.html#rule-silence
    def test_silence_rule(self):
        """
        $ trash-put foo
        """
        self.sandbox.create_file('foo')
        self.sandbox.execute("trash-put","foo").assert_result(output="")
            
    def test_dot_argument_is_skipped(self):
        """
        $ trash-put . other_argument
        trash-put: cannot trash directory `.'
        """
        self.sandbox.create_file('other_argument')
        result = self.sandbox.execute("trash-put", ".","other_argument")
        
        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be writtend on stderr
        print result.stderr
        assert_equals(result.stderr,"trash-put: cannot trash directory `.'\n")
        
        # the remaining arguments should be processed
        assert_false(self.sandbox.path.join('other_argument').exists())

    def test_dot_dot_argument_is_skipped(self):
        """
        $ trash-put .. other_argument
        trash-put: cannot trash directory `..'
        """
        self.sandbox.create_file('other_argument')
        result = self.sandbox.execute("trash-put", "..", "other_argument")
        
        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be writtend on stderr
        
        assert_equals(result.stderr,"trash-put: cannot trash directory `..'\n")
        
        # the remaining arguments should be processed
        assert_false(self.sandbox.path.join('other_argument').exists())
    
    def test_dot_argument_is_skipped_even_in_subdirs(self):
        """
        $ trash-put foo/. other_argument
        trash-put: cannot trash directory `.'
        """
        self.sandbox.path.join('foo').mkdir()
        self.sandbox.create_file('other_argument')
        result = self.sandbox.execute("trash-put", "foo/.","other_argument")
        
        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be writtend on stderr
        assert_equals(result.stderr,
            "trash-put: cannot trash `.' directory `foo/.'\n")
        
        # the remaining arguments should be processed
        assert_false(self.sandbox.path.join('other_argument').exists())
        assert_true(self.sandbox.path.join('foo').exists())

    def test_dot_dot_argument_is_skipped_even_in_subdirs(self):
        """
        $ trash-put foo/.. other_argument
        trash-put: cannot trash directory `..'
        """
        self.sandbox.path.join('foo').mkdir()
        self.sandbox.create_file('other_argument')
        result = self.sandbox.execute("trash-put", "foo/..", "other_argument")
        
        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be writtend on stderr
        assert_equals(result.stderr,
            "trash-put: cannot trash `..' directory `foo/..'\n")
        
        # the remaining arguments should be processed
        assert_false(self.sandbox.path.join('other_argument').exists())
        assert_true(self.sandbox.path.join('foo').exists())
    