from unittest import TestCase

restore_cmd='/home/andrea/trash-cli/scripts/trash-restore'

class ExecutionResult:
    """
    self.exit_code: integer
    self.stdout_data: string
    self.stderr_data: string
    """
    def __init__(self, exit_code, stdout_data, stderr_data):
        self.exit_code = exit_code
        self.stdout_data = stdout_data
        self.stderr_data = stderr_data

def execute_command(args):
    from subprocess import Popen
    from subprocess import PIPE
    proc = Popen(args, stdout=PIPE, stderr=PIPE)
    (stdout_data,stderr_data) = proc.communicate()
    proc.wait()
    print "out:" + stdout_data
    print "exit_code:", proc.returncode
    print "stderr_data:\n", stderr_data, "\n\n"
    return ExecutionResult(proc.returncode, stdout_data, stderr_data)

class RestoreTest(TestCase):
    def test_version_option(self):
        import re
        result = execute_command([restore_cmd,'--version'])
        assert result.exit_code == 0
        assert result.stderr_data == ""
        expected = re.compile("trash-restore (\d)+\.(\d)+\.(\d)+")
        assert expected.match(result.stdout_data) is not None
    