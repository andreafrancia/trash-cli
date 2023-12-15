from typing import List
from typing import NamedTuple
from typing import Optional

from tests.run_command import CmdResult
from tests.run_command import grep
from tests.run_command import run_command
from tests.support.help_reformatting import reformat_help_message
from tests.support.my_path import MyPath
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

    def grep(self, pattern):
        return Stream(stream=grep(self.stream, pattern),
                      temp_dir=self.temp_dir)

    def replace(self, old, new):
        return Stream(stream=self.stream.replace(old, new),
                      temp_dir=self.temp_dir)


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


def run_trashput_with_vol(temp_dir,  # type: MyPath
                          fake_vol,  # type: MyPath
                          args,  # type: List[str]
                          ):  # type: (...) -> Stream
    result = run_trash_put2(temp_dir,
                            ["--force-volume=%s" % fake_vol, '-v'] + args,
                            env=with_uid(123))
    output = result.both().replace(fake_vol, "/vol")
    return output


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


def with_uid(uid):
    return {'TRASH_PUT_FAKE_UID_FOR_TESTING': str(uid)}
