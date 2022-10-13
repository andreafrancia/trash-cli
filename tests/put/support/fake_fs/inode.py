class INode:
    def __init__(self, file_or_dir, mode, sticky):
        self.file_or_dir = file_or_dir
        self.mode = mode
        self.sticky = sticky

    def chmod(self, mode):
        self.mode = mode


class SymLink:
    def __init__(self, dest):
        self.dest = dest
