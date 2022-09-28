from io import StringIO


class MyLogger:
    def __init__(self,
                 stderr,  # type: StringIO
                 verbose,  # type: int
                 ): # type: (...) -> None
        self.stderr = stderr
        self.verbose = verbose

    def debug(self, message, program_name): # type: (str, str) -> None
        if self.verbose > 1:
            self.stderr.write("%s: %s\n" % (program_name, message))

    def debug_func_result(self, messages_func, program_name):
        if self.verbose > 1:
            for line in messages_func():
                self.stderr.write("%s: %s\n" % (program_name, line))

    def info(self, message, program_name):
        if self.verbose > 0:
            self.stderr.write("%s: %s\n" % (program_name, message))

    def warning2(self, message, program_name):
        self.stderr.write("%s: %s\n" % (program_name, message))
