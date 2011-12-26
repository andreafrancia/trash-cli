# Copyright (C) 2009-2011 Andrea Francia Trivolzio(PV) Italy

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

