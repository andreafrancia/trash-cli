from io import StringIO

from typing import IO


class MyLogger:
    def __init__(self,
                 stderr,  # type: IO[str]
                 ):  # type: (...) -> None
        self.stderr = stderr

    def debug(self, message, program_name, verbose):  # type: (str, str) -> None
        if verbose > 1:
            self.stderr.write("%s: %s\n" % (program_name, message))

    def debug_func_result(self, messages_func, program_name, verbose):
        if verbose > 1:
            for line in messages_func():
                self.stderr.write("%s: %s\n" % (program_name, line))

    def info(self, message, program_name, verbose):
        if verbose > 0:
            self.stderr.write("%s: %s\n" % (program_name, message))

    def warning2(self, message, program_name):
        self.stderr.write("%s: %s\n" % (program_name, message))
