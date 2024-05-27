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
        self.fs.make_text_file("trashcli/trash.py", "version = ...")

        result = self.run.run_cmd(['master', '12345b'], capsys)

        assert result == (
            'exit code: None\n'
            'stderr: \n'
            'stdout: \n'
            'filesystem:\n'
            "  /trashcli/trash.py: version = '0.24.5.13.dev0+git.master.12345b'"
        )

    def test(self, capsys):
        self.fs.mkdir("trashcli")
        self.fs.make_text_file("trashcli/trash.py", "version = ...")

        result = self.run.run_cmd(['-', '12345b'], capsys)

        assert result == (
            'exit code: 1\n'
            "stderr: Ref cannot contain '-': -\n"
            "The reason is because any '-' will be converted to '.' by "
            "setuptools during the egg_info phase that will result in an "
            "error in scripts/make-scripts because it will be not able to "
            "find the .tar.gz file\n\n"
            'stdout: \n'
            'filesystem:\n'
            '  /trashcli/trash.py: version = ...')
