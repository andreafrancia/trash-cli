TARGET_HOST = '192.168.56.101'

def main():
    import nose
    nose.runmodule()

from nose.tools import assert_equals, assert_not_equals
import subprocess

from trashcli.trash import version

class TestInstallation:
    def setUp(self):
        self.ssh = Connection('root@' + TARGET_HOST)
        self.executables = [
                'trash-put', 'trash-list', 'trash-rm', 'trash-empty',
                'restore-trash', 'trash']
        self.uninstall_software()
        self.install_software()
    def uninstall_software(self):
        for executable in self.executables:
            self._remove_executable(executable)
            self._assert_command_removed(executable)
    def _assert_command_removed(self, executable):
        result = self.ssh.run('which %s' % executable)
        command_not_existent_exit_code_for_which = 1
        assert_equals(result.exit_code, command_not_existent_exit_code_for_which,
                      'Which returned: %s\n' % result.exit_code +
                      'and reported: %s' % result.stdout
                      )
    def _remove_executable(self, executable):
        self.ssh.run('rm -f $(which %s)' % executable).assert_succesful()
    def install_software(self):
        tarball="trash-cli-%s.tar.gz" % version
        self.ssh.put('dist/%(tarball)s' % locals())
        self.ssh.run('tar xvfz %(tarball)s' % locals())
        self.ssh.run('cd %s && python setup.py install'
                % strip_end(tarball, '.tar.gz')).assert_succesful()
    def test_should_install_all_commands(self):
        for command in self.executables:
            result = self.ssh.run('%(command)s --version' % locals())
            assert_not_equals(127, result.exit_code,
                    "Probably command not found, command: %s" % command)

def strip_end(text, suffix):
    if not text.endswith(suffix):
        return text
    return text[:-len(suffix)]

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
            assert self.exit_code == 0

class TestConnection:
    def __init__(self):
        self.ssh = Connection(TARGET_HOST)
    def test_should_report_stdout(self):
        result = self.ssh.run('echo', 'foo')
        assert_equals('foo\n', result.stdout)
    def test_should_report_stderr(self):
        result = self.ssh.run('echo bar 1>&2')
        assert_equals('bar\n', result.stderr)
    def test_should_report_exit_code(self):
        result = self.ssh.run("exit 134")
        assert_equals(134, result.exit_code)

if __name__ == '__main__':
    main()
