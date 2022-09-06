class Errors:
    def __init__(self, program_name, err):
        self.program_name = program_name
        self.err = err

    def print_error(self, msg):
        self.err.write("%s: %s\n" % (self.program_name, msg))
