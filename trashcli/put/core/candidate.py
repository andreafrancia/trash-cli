import os
from typing import NamedTuple

from trashcli.lib.shrink_user import shrink_user
from trashcli.put.core.check_type import CheckType
from trashcli.put.core.path_maker_type import PathMakerType
from trashcli.put.gate import Gate


class Candidate(NamedTuple('Candidate', [
    ('trash_dir_path', str),
    ('volume', str),
    ('path_maker_type', PathMakerType),
    ('check_type', CheckType),
    ('gate', Gate),
])):
    def parent_dir(self):
        return os.path.dirname(self.trash_dir_path)

    def info_dir(self):
        return os.path.join(self.trash_dir_path, 'info')

    def files_dir(self):
        return os.path.join(self.trash_dir_path, 'files')

    def norm_path(self):
        return os.path.normpath(self.trash_dir_path)

    def shrink_user(self, environ):
        if environ.get('TRASH_PUT_DISABLE_SHRINK', '') == '1':
            return self.norm_path()
        return shrink_user(self.norm_path(), environ)
