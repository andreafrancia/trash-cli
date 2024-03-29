from trashcli.put.context import Context
from trashcli.put.core.trash_all_result import TrashAllResult
from trashcli.put.core.trash_result import TrashResult
from trashcli.put.my_logger import MyLogger
from trashcli.put.trasher import Trasher


class TrashAll:
    def __init__(self,
                 logger,  # type: MyLogger
                 trasher,  # type: Trasher
                 ):  # type: (...) -> None
        self.logger = logger
        self.trasher = trasher

    def trash_all(self,
                  context,  # type: Context
                  ):  # (...) -> Result
        failed_paths = []
        for path in context.paths:
            result = self.trasher.trash_single(path, context)
            if result == TrashResult.Failure:
                failed_paths.append(path)

        return TrashAllResult(failed_paths)
