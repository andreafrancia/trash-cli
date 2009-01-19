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

class Command(object):
    def __init__(self, cmdline, env={}):
        """
        cmdline: the command line (list of string or string)
        env: a map of enviroment variables
        """
        self.cmdline = cmdline
        if not isinstance(env, dict): 
            raise TypeError("env should be a map")
        self.env = env
    
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
    