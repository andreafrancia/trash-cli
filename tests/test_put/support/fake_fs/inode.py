from tests.test_put.support.fake_fs.ent import Ent


class INode:
    def __init__(self, mode, sticky):
        self.mode = mode
        self.sticky = sticky
        self.file_or_dir = None

    def set_file_or_dir(self, file_or_dir):  # type: (Ent)->None
        self.file_or_dir = file_or_dir

    def chmod(self, mode):
        self.mode = mode
