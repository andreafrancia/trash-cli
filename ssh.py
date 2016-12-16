from nose.tools import assert_equals
import subprocess

class Connection:
    def __init__(self, target_host):
        self.target_host = target_host
    def run(self, *user_command):
        ssh_invocation = ['ssh', self.target_host, '-oVisualHostKey=false']
        command = ssh_invocation + list(user_command)
        exit_code, stderr, stdout = self._run_command(command)
        return self.ExecutionResult(stdout, stderr, exit_code)
    def put(self, source_file):
        scp_command = ['scp', source_file, self.target_host + ':']
        exit_code, stderr, stdout = self._run_command(scp_command)
        assert 0 == exit_code
    def _run_command(self, command):
        process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout,stderr = process.communicate()
        exit_code = process.poll()
        return exit_code, stderr, stdout
    class ExecutionResult:
        def __init__(self, stdout, stderr, exit_code):
            self.stdout = stdout
            self.stderr = stderr
            self.exit_code = exit_code
        def assert_no_err(self):
            assert_equals('', self.stderr)
        def assert_succesful(self):
            assert self.exit_code == 0, "Failed:\n - stderr:%s" % self.stderr


