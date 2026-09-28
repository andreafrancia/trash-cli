class SymLink:
    def __init__(self, dest):
        self.dest = dest
        self.mode = 0o777

    def __repr__(self):
        return "SymLink(%r)" % self.dest
