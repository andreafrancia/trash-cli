from logging import Logger

from trashcli.restore.restore_logger import RestoreLogger


class RealRestoreLogger(RestoreLogger):
    def __init__(self,
                 logger,  # type: Logger
                 ):
        self._logger = logger

    def warning(self, message):
        self._logger.warning(message)
