# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
from __future__ import absolute_import

import pwd
from typing import Union

from trashcli.lib.trash_dirs import (
    home_trash_dir_path_from_env,
    home_trash_dir_path_from_home)


class UserInfo:
    def __init__(self, home_trash_dir_paths, uid):
        self.home_trash_dir_paths = home_trash_dir_paths
        self.uid = uid


class SingleUserInfoProvider:
    @staticmethod
    def get_user_info(environ, uid):
        return [UserInfo(home_trash_dir_path_from_env(environ), uid)]


class AllUsersInfoProvider:
    @staticmethod
    def get_user_info(_environ, _uid):
        for user in pwd.getpwall():
            yield UserInfo([home_trash_dir_path_from_home(user.pw_dir)],
                           user.pw_uid)


UserInfoProvider = Union[SingleUserInfoProvider, AllUsersInfoProvider]
