import os
import subprocess
import sys
from typing import List
from typing import NamedTuple
from typing import Optional

import pytest

from scripts.make_scripts import script_path_for
from tests.support.help_reformatting import reformat_help_message
from tests.support.my_path import MyPath
from trashcli import base_dir
from trashcli.lib.environ import Environ


class Stream(NamedTuple('Output', [
    ('stream', str),
    ('temp_dir', MyPath)
])):
    def lines(self):
        return self.stream.replace(self.temp_dir, '').splitlines()

    def last_line(self):
        return self.lines()[-1]

    def first_line(self):
        return self.lines()[0]

    def cleaned(self):
        return self.stream.replace(self.temp_dir, '')

    def describe_stream(self):  # type: () -> str
        if len(self.stream) == 0:
            return "empty"
        else:
            return repr(self.stream)


class PutResult(NamedTuple('Output', [
    ('stderr', Stream),
    ('stdout', Stream),
    ('exit_code', int),
    ('temp_dir', MyPath),
])):
    def help_message(self):
        return reformat_help_message(self.stdout.stream)

    def combined(self):
        return [self.stderr.cleaned() +
                self.stdout.cleaned(),
                self.exit_code]

    def status(self):
        return ["output is %s" % self.both().describe_stream(),
                "exit code is %s" % self.exit_code]

    def both(self):
        return Stream(stream=self.stderr.stream + self.stdout.stream,
                      temp_dir=self.temp_dir)

    def messages(self):
        return self.both().cleaned()


class CmdResult:
    def __init__(self,
                 stdout,  # type: str
                 stderr,  # type: str
                 exit_code,  # type: int
                 ):  # (...) -> None
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.all = [stdout, stderr, exit_code]

    def __str__(self):
        return str(self.all)

    def output(self):
        return self._format([self.stdout, self.stderr])

    def last_line_of_stderr(self):
        return last_line_of(self.stderr)

    def last_line_of_stdout(self):
        return last_line_of(self.stdout)

    def reformatted_help(self):
        return reformat_help_message(self.stdout)

    @staticmethod
    def _format(outs):
        outs = [out for out in outs if out != ""]
        return "".join([out.rstrip("\n") + "\n" for out in outs])

    def clean_vol_and_grep(self,
                           pattern,  # type: str
                           fake_vol,  # type: MyPath
                           ):  # type: (...) -> List[str]

        matching_lines = self._grep(self.stderr, pattern)
        return matching_lines.replace(fake_vol, "/vol").splitlines()

    @staticmethod
    def _grep(stream, pattern):  # type: (str, str) -> str
        return ''.join([line
                        for line in stream.splitlines(True)
                        if pattern in line])

    def clean_temp_dir(self, temp_dir):  # type: (MyPath) -> str
        return self.stderr.replace(temp_dir, "")

    def clean_tmp_and_grep(self,
                           temp_dir,  # type: MyPath
                           pattern,  # type: str
                           ):  # type: (...) -> str
        return self._grep(self.clean_temp_dir(temp_dir), pattern)


def run_command(cwd, command, args=None, input='', env=None):
    if env is None:
        env = {}
    if args is None:
        args = []
    command_full_path = script_path_for(command)
    env['PYTHONPATH'] = base_dir
    process = subprocess.Popen([sys.executable, command_full_path] + args,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               cwd=cwd,
                               env=merge_dicts(os.environ, env))
    stdout, stderr = process.communicate(input=input.encode('utf-8'))

    return CmdResult(stdout.decode('utf-8'),
                     stderr.decode('utf-8'),
                     process.returncode)


def run_trash_put(tmp_dir,  # type: MyPath
                  args,  # type: List[str]
                  env=None,  # type: Optional[Environ]
                  ):  # type: (...) -> PutResult
    extra_args = [
        '-v',
        '--trash-dir', tmp_dir / 'trash-dir',
    ]
    env = env or {}
    return run_trash_put2(tmp_dir, extra_args + args, env=env)


def run_trash_put2(tmp_dir,  # type: MyPath
                   args,  # type: List[str]
                   env,  # type: Environ
                   ):  # type: (...) -> PutResult

    result = run_command(tmp_dir, 'trash-put',
                         args, env=env)

    return make_put_result(result, tmp_dir)


def make_put_result(result,  # type: CmdResult
                    temp_dir,  # type: MyPath
                    ):  # type: (...) -> PutResult
    return PutResult(stdout=Stream(stream=result.stdout, temp_dir=temp_dir),
                     stderr=Stream(stream=result.stderr, temp_dir=temp_dir),
                     exit_code=result.exit_code,
                     temp_dir=temp_dir)


@pytest.fixture
def temp_dir():
    temp_dir = MyPath.make_temp_dir()
    yield temp_dir
    temp_dir.clean_up()


def merge_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z


def last_line_of(stdout):
    if len(stdout.splitlines()) > 0:
        return stdout.splitlines()[-1]
    else:
        return ''
