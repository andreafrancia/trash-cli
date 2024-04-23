from tests.support.help.help_reformatting import reformat_help_message
from tests.support.text.last_line_of import last_line_of


class CmdResult:
    def __init__(self,
                 stdout,  # type: str
                 stderr,  # type: str
                 exit_code,  # type: int
                 ):  # (...) -> None
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.all = (stdout, stderr, exit_code)

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
