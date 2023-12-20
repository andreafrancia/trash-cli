from tests.test_put.support.fake_fs.ent import Ent


class SymLink(Ent):
    def __init__(self, dest):
        self.dest = dest

    def __repr__(self):
        return "SymLink(%r)" % self.dest
