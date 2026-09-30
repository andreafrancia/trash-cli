import os
import shutil

from trashcli.fslib.protocols.remove_file2 import RemoveFile2


class RealRemoveFile2(RemoveFile2):
    def remove_file2(self, path):
        try:
            os.remove(path)
        except OSError:
            shutil.rmtree(path)
