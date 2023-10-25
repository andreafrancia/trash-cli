from trashcli.put.core.trash_all_result import TrashAllResult
from trashcli.put.my_logger import MyLogger, LogData
from trashcli.put.core.trash_result import TrashResult
from trashcli.put.trasher import Trasher


class TrashAll:
    def __init__(self,
                 logger,  # type: MyLogger
                 trasher,  # type: Trasher
                 ):  # type: (...) -> None
        self.logger = logger
        self.trasher = trasher

    def trash_all(self,
                  paths,
                  user_trash_dir,
                  mode,
                  forced_volume,
                  home_fallback,
                  program_name,
                  log_data,  # type: LogData
                  environ,
                  uid,
                  ):  # (...) -> Result
        failed_paths = []
        for path in paths:
            result = self.trasher.trash_single(path,
                                               user_trash_dir,
                                               mode,
                                               forced_volume,
                                               home_fallback,
                                               program_name,
                                               log_data,
                                               environ,
                                               uid)
            if result == TrashResult.Failure:
                failed_paths.append(path)

        return TrashAllResult(failed_paths)
