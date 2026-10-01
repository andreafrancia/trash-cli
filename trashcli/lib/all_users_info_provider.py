from __future__ import absolute_import

from trashcli.lib.protocols.get_all_users import GetPwAll
from trashcli.lib.trash_dirs import home_trash_dir_path_from_home
from trashcli.lib.user_info import UserInfo
from trashcli.lib.user_info_provider import UserInfoProvider


class AllUsersInfoProvider(UserInfoProvider):
    def __init__(self,
                 pwd,  # type: GetPwAll
                 ):
        self.pwd = pwd

    def get_user_info(self, environ, uid):
        for pw in self.pwd.get_pw_all():
            yield UserInfo([home_trash_dir_path_from_home(pw.pw_dir)],
                           pw.pw_uid)
