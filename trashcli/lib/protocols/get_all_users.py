from abc import abstractmethod
from typing import Iterable

from trashcli.compat import Protocol
from trashcli.lib.protocols.pwd_user import PwdUser


class GetPwAll(Protocol):
    @abstractmethod
    def get_pw_all(self):  # type: ()-> Iterable[PwdUser]
        raise NotImplementedError()
