class INode:
    def __init__(self, mode, sticky):
        self.mode = mode
        self.sticky = sticky

    def set_file_or_dir(self, file_or_dir):
        self.file_or_dir = file_or_dir

    def chmod(self, mode):
        self.mode = mode


class SymLink:
    def __init__(self, dest):
        self.dest = dest
