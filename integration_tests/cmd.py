# Copyright (C) 2009-2011 Andrea Francia Trivolzio(PV) Italy

from nose.tools import assert_equals
from assert_equals_with_unidiff import assert_equals_with_unidiff

class CmdResult(object):

    """
    self.exit_code: integer
    self.stdout_data: string
    self.stderr_data: string
    """
    def __init__(self, exit_code, stdout_data, stderr_data):
        self.exit_code = exit_code
        self.stdout = stdout_data
        self.stderr = stderr_data

    def assert_result(self, exit_code=None, output=None, error=None):
        if output != None:
            assert_equals_with_unidiff(self.stdout, output)
        if error != None:
            assert_equals(self.stderr, error)
        if exit_code != None:
            assert_equals(self.exit_code, exit_code)

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

class CommandEnviroment():
    """
    Run commands for the same working dir and enviroments
    """
    def __init__(self, cmd_aliases, cwd=".", env={}):
        self.cmd_aliases=cmd_aliases
        self.cwd=cwd
        self.env=env

    def run(self, cmd, *args) :
        """
        Run a Command.

        The Command is created on the fly using the self.cmd() method.
        """
        return self.cmd(cmd,*args).run()

    def cmd(self, cmd, *args) :
        """
        Creates a command.

        The 'cmd' is subsituted should be present in cmd_aliases.
        The command is run in the current enviroment (self.env) in the current directory (self.cwd)
        It returns the CommandResult of the command.
        """
        import os
        if os.path.isabs(cmd):
            real_cmd = cmd
        else:
            real_cmd =self.cmd_aliases[cmd]
        cmd_line = [real_cmd] + list(args)
        return Command(cmd_line, self.env, self.cwd)


