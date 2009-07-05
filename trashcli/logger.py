import sys

class Logger(object):
    def reply(self, message):
        raise NotImplementedError()

    def info(self, message):
        raise NotImplementedError()

    def warning(self, message):
        raise NotImplementedError()

    def error(self, message):
        raise NotImplementedError()

    def fatal(self, message):
        raise NotImplementedError()

class ConsoleLogger(object):
    def reply(self, message):
        sys.stdout.write(message + '\n')

    def info(self, message):
        sys.stdout.write(message + '\n')

    def warning(self, message):
        sys.stderr.write(message + '\n')

    def error(self, message):
        sys.stderr.write(message + '\n')

    def fatal(self, message):
        sys.stderr.write(message + '\n')

class MemoryLogger(object):
    """
    Log messages to memory for subsequent use
    """

    def __init__(self):
        self.messages = []

    def reply(self, message):
        self.messages.append(("reply", message))
    def info(self, message):
        self.messages.append(("info", message))

    def warning(self, message):
        self.messages.append(("warning", message))

    def error(self, message):
        self.messages.append(("error", message))

    def fatal(self, message):
        self.messages.append(("fatal", message))
