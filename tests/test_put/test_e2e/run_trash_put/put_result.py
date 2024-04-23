from typing import NamedTuple

from tests.support.run.cmd_result import CmdResult
from tests.support.help.help_reformatting import reformat_help_message
from tests.support.dirs.my_path import MyPath
from tests.test_put.test_e2e.run_trash_put.stream import Stream


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

def make_put_result(result,  # type: CmdResult
                    temp_dir,  # type: MyPath
                    ):  # type: (...) -> PutResult
    return PutResult(stdout=Stream(stream=result.stdout, temp_dir=temp_dir),
                     stderr=Stream(stream=result.stderr, temp_dir=temp_dir),
                     exit_code=result.exit_code,
                     temp_dir=temp_dir)
