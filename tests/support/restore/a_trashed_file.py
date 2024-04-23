from typing import NamedTuple


def a_trashed_file(trashed_from, info_file, backup_copy):
    return ATrashedFile(trashed_from=str(trashed_from),
                        info_file=str(info_file),
                        backup_copy=str(backup_copy))


class ATrashedFile(NamedTuple('ATrashedFile', [
    ('trashed_from', str),
    ('info_file', str),
    ('backup_copy', str),
])):
    pass
