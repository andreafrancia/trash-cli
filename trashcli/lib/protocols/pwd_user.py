from typing import NamedTuple


class PwdUser(NamedTuple('PwdUser', [
    ('pw_dir', str),
    ('pw_uid', int),
])):
    pass
