from tests.support.put.fake_fs.ent import Ent
from tests.support.put.fake_fs.stickiness import Stickiness
from trashcli.put.check_cast import check_cast


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

    def directory(self):
        from tests.support.put.fake_fs.directory import Directory
        return check_cast(Directory, self.entity)
