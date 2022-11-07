import os
import posixpath
import re

from typing import NamedTuple, Type

from trashcli.put.gate import Gate


class Candidate(NamedTuple('Candidate', [
    ('trash_dir_path', str),
    ('volume', str),
    ('path_maker_type', str),
    ('check_type', str),
    ('gate', Type[Gate]),
])):
    def info_dir(self):
        return os.path.join(self.trash_dir_path, 'info')

    def files_dir(self):
        return os.path.join(self.trash_dir_path, 'files')

    def norm_path(self):
        return os.path.normpath(self.trash_dir_path)

    def shrink_user(self, environ):
        path = self.norm_path()
        home_dir = environ.get('HOME', '')
        home_dir = posixpath.normpath(home_dir)
        if home_dir != '':
            path = re.sub('^' + re.escape(home_dir + os.path.sep),
                          '~' + os.path.sep, path)
        return path
