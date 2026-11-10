from abc import abstractmethod

from trashcli.compat import Protocol


class ForceRemover(Protocol):
    @abstractmethod
    def remove_path_forcefully(self, path):
        raise NotImplementedError()
