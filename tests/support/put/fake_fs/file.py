from tests.support.put.fake_fs.ent import Ent


class File(Ent):
    def __init__(self, content):
        self.content = content

    def getsize(self):
        return len(self.content)
