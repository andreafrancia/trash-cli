class Console:
    def __init__(self, errors):
        self.errors = errors

    def print_cannot_remove_error(self, path):
        self.errors.print_error("cannot remove %s" % path)
