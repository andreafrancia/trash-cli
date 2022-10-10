class Entry:
    def __init__(self, file, mode, sticky):
        self.file = file
        self.mode = mode
        self.sticky = sticky

class SymLink:
    def __init__(self, dest):
        self.dest = dest
