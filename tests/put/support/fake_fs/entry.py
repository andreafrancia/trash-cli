class Entry:
    def __init__(self, file, mode):
        self.file = file
        self.mode = mode

class SymLink:
    def __init__(self, dest):
        self.dest = dest
