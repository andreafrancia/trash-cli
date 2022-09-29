from trashcli.put.my_logger import MyLogger
from trashcli.put.reporter import TrashPutReporter
from trashcli.put.trash_result import TrashResult
from trashcli.put.trasher import Trasher


class TrashAll:
    def __init__(self,
                 logger,  # type: MyLogger
                 trasher,  # type: Trasher
                 reporter,  # type: TrashPutReporter
                 ):  # type: (...) -> None
        self.logger = logger
        self.trasher = trasher
        self.reporter = reporter

    def trash_all(self,
                  args,
                  user_trash_dir,
                  mode,
                  forced_volume,
                  program_name,
                  verbose,
                  environ,
                  uid):
        result = TrashResult(False)
        for arg in args:
            result = self.trasher.trash(arg,
                                        user_trash_dir,
                                        result,
                                        mode,
                                        self.reporter,
                                        forced_volume,
                                        program_name,
                                        verbose,
                                        environ,
                                        uid)
        return result
