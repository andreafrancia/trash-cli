class INode:
    def __init__(self, mode, sticky):
        self.mode = mode
        self.sticky = sticky

    def set_file_or_dir(self, file_or_dir):
        self.file_or_dir = file_or_dir

    def chmod(self, mode):
        self.mode = mode

    @staticmethod
    def make_inode_for_file(mode, file):
        inode = INode(mode, sticky=False)
        inode.set_file_or_dir(file)
        return inode

class SymLink:
    def __init__(self, dest):
        self.dest = dest
