from typing import List
from trashcli.compat import Protocol


class ListdirFs(Protocol):
    def listdir(self, path):  # type: (str) -> List[str]
        pass
