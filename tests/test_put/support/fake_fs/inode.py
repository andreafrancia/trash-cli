from enum import Enum
from typing import Optional
from tests.test_put.support.fake_fs.ent import Ent


class Stickiness(Enum):
    sticky = "sticky"
    not_sticky = "not_sticky"


class INode:
    def __init__(self,
                 entity,  # type: Ent
                 mode,  # type: int
                 stickiness,  # type: Stickiness
                 ):
        self.entity = entity
        self.mode = mode
        self.stickiness = stickiness

    def chmod(self, mode):
        self.mode = mode

    def __repr__(self):
        return "INode(%r, %r, %r)" % (self.entity, self.mode, self.stickiness)
