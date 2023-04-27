class ListCmdOutput:
    def __init__(self, out, err):
        self.out = out
        self.err = err

    def println(self, line):
        self.out.write(line + '\n')

    def error(self, line):
        self.err.write(line + '\n')

    def print_read_error(self, error):
        self.error(str(error))

    def print_parse_path_error(self, offending_file):
        self.error("Parse Error: %s: Unable to parse Path." % (offending_file))

    def top_trashdir_skipped_because_parent_not_sticky(self, trashdir):
        self.error("TrashDir skipped because parent not sticky: %s"
                   % trashdir)

    def top_trashdir_skipped_because_parent_is_symlink(self, trashdir):
        self.error("TrashDir skipped because parent is symlink: %s"
                   % trashdir)
