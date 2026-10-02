from abc import abstractmethod
from trashcli.compat import Protocol

class AbspathFs(Protocol):
    @abstractmethod
    def abspath(self,
                path,  # type: str
                ):
        raise NotImplementedError
