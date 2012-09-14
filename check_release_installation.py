TARGET_HOST = '192.168.56.101'

import nose
from nose.tools import assert_equals, assert_not_equals
from ssh import Connection

from trashcli.trash import version

def main():
    check_connection()
    check_installation(normal_installation)
    check_installation(easy_install_installation)

def check_installation(installation_method):
    tc = LinuxBox('root@' + TARGET_HOST, installation_method)
    print "== Cleaning any prior software installation"
    tc.clean_any_prior_installation()
    print "== Copying software"
    tc.copy_tarball()
    print "== Installing software"
    tc.install_software()
    print "== Checking all program were installed"
    tc.check_all_programs_are_installed()


class LinuxBox:
    def __init__(self, address, installation_method):
        self.ssh = Connection(address)
        self.executables = [
                'trash-put', 'trash-list', 'trash-rm', 'trash-empty',
                'restore-trash', 'trash']
        self.tarball="trash-cli-%s.tar.gz" % version
        self.installation_method = installation_method
    def clean_any_prior_installation(self):
        "clean any prior installation"
        for executable in self.executables:
            self._remove_executable(executable)
            self._assert_command_removed(executable)
    def _remove_executable(self, executable):
        self.ssh.run('rm -f $(which %s)' % executable).assert_succesful()
    def _assert_command_removed(self, executable):
        result = self.ssh.run('which %s' % executable)
        command_not_existent_exit_code_for_which = 1
        assert_equals(result.exit_code, command_not_existent_exit_code_for_which,
                      'Which returned: %s\n' % result.exit_code +
                      'and reported: %s' % result.stdout
                      )
    def copy_tarball(self):
        self.ssh.put('dist/%s' % self.tarball)
    def install_software(self):
        def run_checked(command):
            result = self.ssh.run(command)
            result.assert_succesful()
        self.installation_method(self.tarball, run_checked)
    def check_all_programs_are_installed(self):
        for command in self.executables:
            result = self.ssh.run('%(command)s --version' % locals())
            assert_not_equals(127, result.exit_code,
                    "Exit code was: %s, " % result.exit_code +
                    "Probably command not found, command: %s" % command)

def normal_installation(tarball, check_run):
    directory = strip_end(tarball, '.tar.gz')
    check_run('tar xfvz %s' % tarball)
    check_run('cd %s && '
              'python setup.py install' % directory)

def easy_install_installation(tarball, check_run):
    check_run('easy_install %s' % tarball)

def strip_end(text, suffix):
    if not text.endswith(suffix):
        return text
    return text[:-len(suffix)]

def check_connection():
    suite = nose.loader.TestLoader().loadTestsFromTestClass(TestConnection)
    nose.run(suite=suite)

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
