import os

from typing import NamedTuple


class Candidate(NamedTuple('Candidate', [
    ('trash_dir_path', str),
    ('volume', str),
    ('path_maker_type', str),
    ('check_type', str),
])):
    def info_dir(self):
        return os.path.join(self.trash_dir_path, 'info')

    def files_dir(self):
        return os.path.join(self.trash_dir_path, 'files')
