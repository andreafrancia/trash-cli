from six import binary_type

from tests.support.put.fake_fs.ent import Ent


class File(Ent):
    def __init__(self,
                 content,  # type: binary_type
                 ):
        self.content = content  # type: binary_type

    def getsize(self):
        return len(self.content)
