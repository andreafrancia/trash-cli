from check_release_installation import (CheckInstallation,
                                        Pip3Installation,
                                        PipInstallation)
from nose.tools import assert_equals
from mock import call

class TestCheckBothInstallations:
    def setUp(self):
        self.calls = []
        outer = self
        class FakeSSH:
            def run_checked(self, command):
                outer.calls.append(call().run_checked(command))
            def put(self, command):
                outer.calls.append(call().put(command))
        self.ssh = FakeSSH()

    def test_python3(self):
        version = '0.17.1.12'
        ci = CheckInstallation(Pip3Installation(), self.ssh, version)
        ci.check_installation()

        assert_equals([
 call().run_checked('sudo rm -f $(which trash-put)'),
 call().run_checked('! which trash-put'),
 call().run_checked('sudo rm -f $(which trash-list)'),
 call().run_checked('! which trash-list'),
 call().run_checked('sudo rm -f $(which trash-rm)'),
 call().run_checked('! which trash-rm'),
 call().run_checked('sudo rm -f $(which trash-empty)'),
 call().run_checked('! which trash-empty'),
 call().run_checked('sudo rm -f $(which trash-restore)'),
 call().run_checked('! which trash-restore'),
 call().run_checked('sudo rm -f $(which trash)'),
 call().run_checked('! which trash'),
 call().put('dist/trash-cli-0.17.1.12.tar.gz'),
 call().run_checked('sudo pip3 install trash-cli-0.17.1.12.tar.gz'),
 call().run_checked('trash-put --version'),
 call().run_checked('trash-list --version'),
 call().run_checked('trash-rm --version'),
 call().run_checked('trash-empty --version'),
 call().run_checked('trash-restore --version'),
 call().run_checked('trash --version')], self.calls)

    def test_pip2_installation(self):
        version = '0.17.1.12'
        i = CheckInstallation(PipInstallation(), self.ssh, version)
        i.check_installation()

        self.maxDiff = None
        assert_equals([
call().run_checked('sudo rm -f $(which trash-put)'),
call().run_checked('! which trash-put'),
call().run_checked('sudo rm -f $(which trash-list)'),
call().run_checked('! which trash-list'),
call().run_checked('sudo rm -f $(which trash-rm)'),
call().run_checked('! which trash-rm'),
call().run_checked('sudo rm -f $(which trash-empty)'),
call().run_checked('! which trash-empty'),
call().run_checked('sudo rm -f $(which trash-restore)'),
call().run_checked('! which trash-restore'),
call().run_checked('sudo rm -f $(which trash)'),
call().run_checked('! which trash'),
call().put('dist/trash-cli-0.17.1.12.tar.gz'),
call().run_checked('sudo pip install trash-cli-0.17.1.12.tar.gz'),
call().run_checked('trash-put --version'),
call().run_checked('trash-list --version'),
call().run_checked('trash-rm --version'),
call().run_checked('trash-empty --version'),
call().run_checked('trash-restore --version'),
call().run_checked('trash --version')], self.calls)

