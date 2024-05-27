class SymLink:
    def __init__(self, dest):
        self.dest = dest
        self.mode = None

    def __repr__(self):
        return "SymLink(%r)" % self.dest
