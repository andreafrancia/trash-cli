from tests.support.capture_exit_code import capture_exit_code
from tests.support.put.fake_fs.fake_fs import FakeFs
from tests.support.tools.bump_cmd import BumpCmd
from tests.test_dev_tools.support.fake_cal import FakeCal
from tests.test_dev_tools.support.fake_system import FakeSystem


class TestBumpCmd:
    def setup_method(self):
        self.system = FakeSystem()
        self.print_calls = []
        self.fs = FakeFs()
        self.cmd = BumpCmd(self.system.os_system, self.print_calls.append,
                           self.fs, FakeCal("2024-05-01"))

    def test_when_dirty(self):
        exit_code = capture_exit_code(lambda: self.cmd.run_bump("/", []))

        assert exit_code == 1
        assert self.print_calls == ['Dirty']
        assert self.system.os_system_calls == ['git diff-index --quiet HEAD']

    def test_when_clean(self):
        self.system.set_clean()
        self.fs.mkdir('trashcli')
        self.fs.make_file('trashcli/trash.py', "version=x.y.x")

        exit_code = capture_exit_code(lambda: self.cmd.run_bump("/", []))

        assert exit_code == None
        assert self.print_calls == []
        assert self.system.os_system_calls == [
            'git diff-index --quiet HEAD',
            'git commit -m "Bump version to \'0.24.5.1\'" -a']
        assert self.fs.read_all_files() == [
            ('/trashcli/trash.py', "version = '0.24.5.1'")]

    def test_when_clean_and_dry_run(self):
        self.system.set_clean()
        self.fs.mkdir('trashcli')
        self.fs.make_file('trashcli/trash.py', "version=x.y.x")

        exit_code = capture_exit_code(
            lambda: self.cmd.run_bump("/", ['--dry-run']))

        assert exit_code == None
        assert self.print_calls == [
            'git commit -m "Bump version to \'0.24.5.1\'" -a']
        assert self.system.os_system_calls == [
            'git diff-index --quiet HEAD']
        assert self.fs.read_all_files() == [
            ('/trashcli/trash.py', "version=x.y.x")]
