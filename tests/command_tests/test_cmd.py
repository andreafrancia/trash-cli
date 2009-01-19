#!/usr/bin/python
# tests/command_tests/test_cmd.py: Unit tests for cmd.py
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

from cmd import Command
from unittest import TestCase
from nose.tools import raises
from nose.tools import assert_equals
from nose.tools import assert_true
from nose.tools import assert_not_equals

class CommandTest(TestCase):
    def test_run_retuns_exit_code(self):
        result=Command("/bin/false").run()
        assert_not_equals(0, result.exit_code)
        
        result=Command("/bin/true").run()
        assert_equals(0, result.exit_code)
    
    def test_run_returns_output(self):
        result=Command(["/bin/echo", "foo"]).run()
        assert_equals("foo\n", result.out_data)
        
        result=Command(["/bin/echo", "-n", "foo"]).run()
        assert_equals("foo", result.out_data)

    def test_run_returns_error_messages(self):
        result=Command(["python", "--bad-option"]).run()
        assert_true(result.err_data.startswith("Unknown option: --"), 
                    "This may fail even if the code works")
    
    def test_run_reads_the_input(self):
        result=Command("cat").run("text")
        assert_equals("text", result.out_data)
    
    def test_run_honors_env(self):
        result=Command("/usr/bin/env",{'VAR':'value'}).run()
        assert_equals('VAR=value\n', result.out_data)
    
    def test_env_empty_by_default(self):
        result=Command("/usr/bin/env").run()
        assert_equals('', result.out_data)

    @raises(TypeError)
    def test_mistake_is_detected(self):
        Command("/bin/ls", "-l") # <-- mistake, correct --> Command(["ls","-l"])
        