from tests.test_put.support.fake_fs.ent import Ent


class INode:
    def __init__(self, mode, sticky):
        self.mode = mode
        self.sticky = sticky
        self.entity = None

    def set_entity(self, entity):  # type: (Ent)->None
        self.entity = entity

    def chmod(self, mode):
        self.mode = mode
