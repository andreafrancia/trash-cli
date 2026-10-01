from __future__ import absolute_import

from trashcli.lib.trash_dirs import home_trash_dir_path_from_env
from trashcli.lib.user_info import UserInfo
from trashcli.lib.user_info_provider import UserInfoProvider


class SingleUserInfoProvider(UserInfoProvider):
    def get_user_info(self, environ, uid):
        return [UserInfo(home_trash_dir_path_from_env(environ), uid)]
