from typing import NamedTuple

Candidate = NamedTuple('Candidate', [
    ('trash_dir_path', str),
    ('volume', str),
    ('path_maker_type', str),
    ('check_type', str),
])
