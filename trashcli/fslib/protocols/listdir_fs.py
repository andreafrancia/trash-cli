from typing import List, Protocol


class ListdirFs(Protocol):
    def listdir(self, path):  # type: (str) -> List[str]
        pass
