from abc import abstractmethod

from trashcli.compat import Protocol


class ListVolumeFs(Protocol):
    @abstractmethod
    def list_volumes(self, environ):  # type (dict) -> Iterable[str]
        raise NotImplementedError()
