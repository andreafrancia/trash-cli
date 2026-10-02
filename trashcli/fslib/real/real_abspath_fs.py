import os

from trashcli.fslib.protocols.abspath_fs import AbspathFs


class RealAbspathFs(AbspathFs):
    def abspath(self, path):
        return os.path.abspath(path)
