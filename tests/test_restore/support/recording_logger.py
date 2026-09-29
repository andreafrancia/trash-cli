from __future__ import print_function

from trashcli.restore.restore_logger import RestoreLogger


class RecordingLogger(RestoreLogger):
    def __init__(self, capturing=None):
        self.captured = [] if capturing is None else capturing

    def warning(self, message):
        self.captured.append("WARN: %s" % message)
