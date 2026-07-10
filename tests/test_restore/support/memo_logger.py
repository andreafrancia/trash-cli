from trashcli.restore.restore_logger import RestoreLogger


class MemoLogger(RestoreLogger):
    def __init__(self):
        self.messages = []

    def warning(self, msg):
        self.messages.append("warning: " + msg)
