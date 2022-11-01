import os

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
