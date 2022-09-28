from io import StringIO


class MyLogger:
    def __init__(self,
                 stderr,  # type: StringIO
                 program_name,  # type: str
                 verbose,  # type: int
                 ): # type: (...) -> None
        self.program_name = program_name
        self.stderr = stderr
        self.verbose = verbose

    def debug(self, message): # type: (str) -> None
        if self.verbose > 1:
            self.stderr.write("%s: %s\n" % (self.program_name, message))

    def debug_func_result(self, messages_func):
        if self.verbose > 1:
            for line in messages_func():
                self.stderr.write("%s: %s\n" % (self.program_name, line))

    def info(self, message):
        if self.verbose > 0:
            self.stderr.write("%s: %s\n" % (self.program_name, message))

    def warning2(self, message):
        self.stderr.write("%s: %s\n" % (self.program_name, message))
