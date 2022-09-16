class Errors:
    def __init__(self, program_name, err):
        self.program_name = program_name
        self.err = err

    def print_error(self, msg):
        self.err.write(format_error_msg(self.program_name, msg))


def format_error_msg(program_name, msg):
    return "%s: %s\n" % (program_name, msg)
