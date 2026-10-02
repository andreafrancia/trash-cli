from __future__ import absolute_import

from abc import abstractmethod

from trashcli.compat import Protocol


class UserInfoProvider(Protocol):
    @abstractmethod
    def get_user_info(self, environ, uid):
        pass
