from __future__ import print_function
from trashcli.restore.trashed_files import RestoreLogger


class CaptureLogger(RestoreLogger):
    def __init__(self, capturing = None):
        self.captured = capturing or []

    def warning(self, message):
        self.captured.append("WARN: %s" % message)
