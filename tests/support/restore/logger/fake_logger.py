from __future__ import print_function
from trashcli.restore.trashed_files import RestoreLogger


class FakeLogger(RestoreLogger):
    def __init__(self, out):
        self.out = out

    def warning(self, message):
        print("WARN: %s" % message, file=self.out)
