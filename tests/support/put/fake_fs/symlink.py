class SymLink:
    def __init__(self, dest):
        self.dest = dest

    def __repr__(self):
        return "SymLink(%r)" % self.dest
