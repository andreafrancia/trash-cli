from tests.support.put.fake_fs.fake_fs import FakeFs
from tests.test_dev_tools.support.run_set_dev_version import RunSetDevVersion


def adjust_py27(output):
    return output.replace("prg: error: too few arguments\n",
                          'prg: error: the following arguments '
                          'are required: ref, sha\n')


class TestSetDevVersionCmd:
    def setup_method(self):
        self.fs = FakeFs()
        self.run = RunSetDevVersion(self.fs)

    def test_when_no_args_fails(self, capsys):
        result = adjust_py27(self.run.run_cmd([], capsys))

        assert result == (
            'exit code: 2\n'
            'stderr: usage: prg [-h] ref sha\n'
            'prg: error: the following arguments are required: ref, sha\n'
            '\n'
            'stdout: \n'
            'filesystem:\n')

    def test_happy_path(self, capsys):
        self.fs.mkdir("trashcli")
        self.fs.write_file("trashcli/trash.py", "version = ...")

        result = self.run.run_cmd(['master', '12345b'], capsys)

        assert result == (
            'exit code: None\n'
            'stderr: \n'
            'stdout: \n'
            'filesystem:\n'
            "  /trashcli/trash.py: version = '0.24.5.13.dev0+git.master.12345b'"
        )

    def test_ref_with_hyphens_is_sanitized(self, capsys):
        self.fs.mkdir("trashcli")
        self.fs.write_file("trashcli/trash.py", "version = ...")

        result = self.run.run_cmd(['fix-build-failure-27', '12345b'], capsys)

        assert result == (
            'exit code: None\n'
            'stderr: \n'
            'stdout: \n'
            'filesystem:\n'
            "  /trashcli/trash.py: version = "
            "'0.24.5.13.dev0+git.fix.build.failure.27.12345b'"
        )
