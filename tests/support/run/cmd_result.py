from typing import Callable
from typing import NamedTuple
from typing import Union

from six import StringIO
from six import text_type

from tests.support.help.help_reformatting import reformat_help_message
from tests.support.text.last_line_of import last_line_of

ExitCode = Union[str, int, None]


class CmdResult(NamedTuple('CmdResult', [
    ('stdout', text_type),
    ('stderr', text_type),
    ('exit_code', ExitCode),
])):
    @property
    def all(self):
        return self.stdout, self.stderr, self.exit_code

    def all_lines(self):
        return set(self.stderr.splitlines() + self.stdout.splitlines())

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

    @staticmethod
    def run_cmd(func,  # type: Callable[[], int]
                stdout,  # type: StringIO
                stderr,  # type: StringIO
                ):  # type: (...) -> CmdResult
        try:
            exit_code = func()  # type: ExitCode
        except SystemExit as e:
            exit_code = e.code

        return CmdResult(stdout.getvalue(),
                         stderr.getvalue(), exit_code)

    def check_stderr_is_empty(self):
        if self.stderr == '':
            return ''
        return "stderr is not empty: %s" % self.stderr

    def check_stderr_is(self,
                        expected,  # type: text_type
                        ):
        if self.stderr == expected:
            return ''
        return "stderr is not as expected: %s != %s" % (expected, self.stderr)
