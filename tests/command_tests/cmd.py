#!/usr/bin/python
# tests/command_tests/cmd.py: Utilities for runnig commands.
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

from nose.tools import assert_equals

class CmdResult(object):
    """
    self.exit_code: integer
    self.stdout_data: string
    self.stderr_data: string
    """
    def __init__(self, exit_code, stdout_data, stderr_data):
        self.exit_code = exit_code
        self.out_data = stdout_data
        self.err_data = stderr_data

    def assert_result(self, exit_code=None, output=None, error=None):
        if exit_code != None:
	    assert_equals(self.exit_code, exit_code)
        if output != None:
            assert_equals(self.out_data, output)
        if error != None:
            assert_equals(self.err_data, error) 
        

class Command(object):
    def __init__(self, cmdline, env={}, cwd=None):
        """
        cmdline: the command line (list of string or string)
        env: a map of enviroment variables
        """
        self.cmdline = cmdline
        if not isinstance(env, dict): 
            raise TypeError("env should be a map")
        self.env = env
        self.cwd = cwd
    
    def run(self,input_=None):
        """
        Execute the command in the current enviroment and return the CmdResult
        """
        from subprocess import Popen
        from subprocess import PIPE
        proc = Popen(self.cmdline, 
                     stdin=PIPE, 
                     stdout=PIPE, 
                     stderr=PIPE, 
                     cwd=self.cwd,
                     env=self.env)
        (stdout_data,stderr_data) = proc.communicate(input_)
        proc.wait()
        return CmdResult(proc.returncode, stdout_data, stderr_data)

    def assert_succeed(self, input=None):
        result=self.run(input)
        if result.exit_code != 0:
            print 'command failed: %s' % str(self.cmdline)
            print 'exit_code=', result.exit_code
            print 'err_data=', result.err_data
            print 'out_data=', result.out_data
            raise AssertionError("The command returns a %s code instead of 0" 
                                 % result.exit_code)
        return result

    def assert_fail(self, input=None):
        result=self.run(input)
        if result.exit_code == 0:
            raise AssertionError("The command returns a 0 exit code instead, "
                                 "while non zero status is expected")
        return result
    
