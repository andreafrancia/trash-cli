from typing import TextIO

from trashcli.empty.errors import format_error_msg
from trashcli.lib.sanitize import sanitize_for_output


class Console:
    def __init__(self, program_name, out,
                 err):  # type: (str, TextIO, TextIO) -> None
        self.program_name = program_name
        self.out = out
        self.err = err

    def print_cannot_remove_error(self, path):
        self.print_error("cannot remove %s" % path)

    def print_error(self, msg):
        self.err.write(format_error_msg(self.program_name,
                                        sanitize_for_output(msg)))

    def print_dry_run(self, path):
        self.out.write("would remove %s\n" % sanitize_for_output(path))

    def print_removing(self, path):
        self.out.write("removing %s\n" % sanitize_for_output(path))
