TARGET_HOST = '192.168.56.101'

import nose
from nose.tools import assert_equals, assert_not_equals
from ssh import Connection

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
                    "Exit code was: %s, " % result.exit_code +
                    "Probably command not found, command: %s" % command)

def strip_end(text, suffix):
    if not text.endswith(suffix):
        return text
    return text[:-len(suffix)]

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
    nose.runmodule()
