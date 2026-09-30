import os
import shutil

from trashcli.fslib.protocols.remove_file import RemoveFile


class RealRemoveFile(RemoveFile):
    def remove_file(self, path):
        if os.path.lexists(path):
            try:
                os.remove(path)
            except:
                return shutil.rmtree(path)
