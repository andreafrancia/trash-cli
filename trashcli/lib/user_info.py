# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
from __future__ import absolute_import


class UserInfo:
    def __init__(self, home_trash_dir_paths, uid):
        self.home_trash_dir_paths = home_trash_dir_paths
        self.uid = uid
