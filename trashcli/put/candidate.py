import os
import posixpath
import re
from typing import NamedTuple, Type

from trashcli.put.gate import Gate
from trashcli.put.path_maker import PathMakerType
from trashcli.put.security_check import CheckType


class Candidate(NamedTuple('Candidate', [
    ('trash_dir_path', str),
    ('volume', str),
    ('path_maker_type', PathMakerType),
    ('check_type', Type[CheckType]),
    ('gate', Gate),
])):
    def info_dir(self):
        return os.path.join(self.trash_dir_path, 'info')

    def files_dir(self):
        return os.path.join(self.trash_dir_path, 'files')

    def norm_path(self):
        return os.path.normpath(self.trash_dir_path)

    def shrink_user(self, environ):
        path = self.norm_path()
        if environ.get('TRASH_PUT_DISABLE_SHRINK', '') == '1':
            return path
        home_dir = environ.get('HOME', '')
        home_dir = posixpath.normpath(home_dir)
        if home_dir != '':
            path = re.sub('^' + re.escape(home_dir + os.path.sep),
                          '~' + os.path.sep, path)
        return path
