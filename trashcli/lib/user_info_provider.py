from __future__ import absolute_import

from abc import abstractmethod

from typing_extensions import Protocol


class UserInfoProvider(Protocol):
    @abstractmethod
    def get_user_info(self, environ, uid):
        pass
