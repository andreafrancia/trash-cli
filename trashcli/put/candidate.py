from typing import NamedTuple

Candidate = NamedTuple('Candidate', [
    ('path', str),
    ('volume', str),
    ('path_maker', str),
    ('check_type', str),
])
