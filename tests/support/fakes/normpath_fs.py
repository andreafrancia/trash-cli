import os

from trashcli.fslib.protocols.abspath_fs import AbspathFs


class NormpathFs(AbspathFs):
    def abspath(self, path):
        return os.path.normpath(path)
