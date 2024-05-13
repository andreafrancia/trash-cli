from io import StringIO
from typing import NamedTuple
from typing import Optional

from tests.support.capture_exit_code import capture_exit_code
from tests.support.put.fake_fs.fake_fs import FakeFs
from tests.support.tools.set_dev_version import SetDevVersionCmd
from tests.test_dev_tools.cmds.test_bump_cmd import FakeCal


class RunSetDevVersion:
    def __init__(self, fs):
        self.fs = fs

    def run_cmd(self, args, capsys):
        stdout = StringIO()
        stderr = StringIO()
        cmd = SetDevVersionCmd(self.fs, stdout, stderr, FakeCal("2024-05-13"))

        code = capture_exit_code(
            lambda: cmd.run_set_dev_version(['prg'] + args, "/"))
        capture = capsys.readouterr()


        result = Result(stdout.getvalue() + capture.out,
                        stderr.getvalue() + capture.err, code)

        return situation(result, self.fs)


class Result(NamedTuple('Result', [
    ('out', str),
    ('err', str),
    ('exit_code', Optional[int]),
])):
    pass


def situation(result,  # type: Result
              fs,  # type: FakeFs
              ):  # type: (...) -> str
    return ("exit code: %s\n" % result.exit_code +
            "stderr: %s\n" % result.err +
            "stdout: %s\n" % result.out +
            "filesystem:\n" +
            "\n".join([
                "  %s: %s" % (path, content)
                for path, content in fs.read_all_files()
            ])
            )
