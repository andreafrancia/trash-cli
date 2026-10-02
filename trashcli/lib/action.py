from abc import abstractmethod

from trashcli.compat import Protocol

class Action(Protocol):
    @abstractmethod
    def run_action(self,
                   args,
                   ):
        raise NotImplementedError