from abc import abstractmethod

from typing import List, Protocol


class ListdirFs(Protocol):
    @abstractmethod
    def listdir(self, path):  # type: (str) -> List[str]
        pass
