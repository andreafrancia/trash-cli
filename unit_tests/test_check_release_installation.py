from check_release_installation import (CheckInstallation,
                                        NormalInstallation,
                                        EasyInstallInstallation)
from nose.tools import assert_equals, assert_raises
from mock import Mock, call

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
        ci = CheckInstallation(NormalInstallation('python3'), self.ssh, version)
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
 call().run_checked('tar xfvz trash-cli-0.17.1.12.tar.gz'),
 call().run_checked('cd trash-cli-0.17.1.12 && sudo python3 setup.py install'),
 call().run_checked('trash-put --version'),
 call().run_checked('trash-list --version'),
 call().run_checked('trash-rm --version'),
 call().run_checked('trash-empty --version'),
 call().run_checked('trash-restore --version'),
 call().run_checked('trash --version')], self.calls)

    def test_easy_install_installation(self):
        version = '0.17.1.12'
        i = CheckInstallation(EasyInstallInstallation(), self.ssh, version)
        i.check_installation()

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
call().run_checked('sudo easy_install trash-cli-0.17.1.12.tar.gz'),
call().run_checked('trash-put --version'),
call().run_checked('trash-list --version'),
call().run_checked('trash-rm --version'),
call().run_checked('trash-empty --version'),
call().run_checked('trash-restore --version'),
call().run_checked('trash --version')], self.calls)

