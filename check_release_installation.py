from __future__ import print_function

import unittest

TARGET_HOST = 'default'

import subprocess

from trashcli.trash import version

def main():
    check_connection()
    ssh = Connection(TARGET_HOST)
    check_both_installations(ssh)

def check_both_installations(ssh):
    l = CheckInstallation(
            Pip3Installation(), ssh, version)
    l.check_installation()
    l = CheckInstallation(
            PipInstallation(), ssh, version)
    l.check_installation()

class CheckInstallation:
    def __init__(self, installation, ssh, version):
        self.ssh = ssh
        self.executables = [
                'trash-put', 'trash-list', 'trash-rm', 'trash-empty',
                'trash-restore', 'trash']
        self.tarball="trash-cli-%s.tar.gz" % version
        self.installation = installation
    def check_installation(self):
        self.clean_any_prior_installation()
        self.copy_tarball()
        self.install_software()
        self.check_all_programs_are_installed()
    def clean_any_prior_installation(self):
        for executable in self.executables:
            self._remove_executable(executable)
            self._assert_command_removed(executable)
    def _remove_executable(self, executable):
        self.ssh.run_checked('sudo rm -f $(which %s)' % executable)
    def _assert_command_removed(self, executable):
        result = self.ssh.run_checked('! which %s' % executable)
    def copy_tarball(self):
        self.ssh.put('dist/%s' % self.tarball)
    def install_software(self):
        self.installation.install(self.tarball, self.ssh)
    def check_all_programs_are_installed(self):
        for command in self.executables:
            result = self.ssh.run_checked('%(command)s --version' % locals())

class PipInstallation:
    def install(self, tarball, ssh):
        ssh.run_checked('sudo pip install %s' % tarball)
class Pip3Installation:
    def install(self, tarball, ssh):
        ssh.run_checked('sudo pip3 install %s' % tarball)

def strip_end(text, suffix):
    if not text.endswith(suffix):
        return text
    return text[:-len(suffix)]

def check_connection():
    suite = unittest.loader.TestLoader().loadTestsFromTestCase(TestConnection)
    unittest.TextTestRunner().run(suite)


class TestConnection(unittest.TestCase):
    def setUp(self):
        self.ssh = Connection(TARGET_HOST)
    def test_should_report_stdout(self):
        result = self.ssh.run('echo', 'foo')
        self.assertEqual(b'foo\n', result.stdout)
    def test_should_report_stderr(self):
        result = self.ssh.run('echo bar 1>&2')
        self.assertEqual(b'bar\n', result.stderr)
    def test_should_report_exit_code(self):
        result = self.ssh.run("exit 134")
        self.assertEqual(134, result.exit_code)

class Connection:
    def __init__(self, target_host):
        self.target_host = target_host
    def run_checked(self, command):
        print(command)
        result = self.run(command)
        result.assert_succesful()
    def run(self, *user_command):
        ssh_invocation = ['ssh', '-Fssh-config', self.target_host, '-oVisualHostKey=false']
        command = ssh_invocation + list(user_command)
        exit_code, stderr, stdout = self._run_command(command)
        return self.ExecutionResult(stdout, stderr, exit_code)
    def put(self, source_file):
        scp_command = ['scp', '-Fssh-config', source_file, self.target_host + ':']
        exit_code, stderr, stdout = self._run_command(scp_command)
        assert 0 == exit_code, stderr
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
        def assert_succesful(self):
            assert self.exit_code == 0, "Failed:\n - stderr:%s" % self.stderr

if __name__ == '__main__':
    main()
