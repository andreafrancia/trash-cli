from io import TextIOWrapper

from trashcli.empty.errors import format_error_msg


class Console:
    def __init__(self, program_name, out,
                 err):  # type: (str, TextIOWrapper, TextIOWrapper) -> None
        self.program_name = program_name
        self.out = out
        self.err = err

    def print_cannot_remove_error(self, path):
        self.print_error("cannot remove %s" % path)

    def print_error(self, msg):
        self.err.write(format_error_msg(self.program_name, msg))
