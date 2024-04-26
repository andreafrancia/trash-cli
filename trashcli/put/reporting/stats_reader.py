# Copyright (C) 2007-2024 Andrea Francia Trivolzio(PV) Italy

import os
from grp import getgrgid
from pwd import getpwuid
from typing import NamedTuple
import re

from trashcli.put.core.either import Either
from trashcli.put.core.either import Left
from trashcli.put.core.either import Right


def gentle_stat_read(path):
    def stats_str(stats):  # type: (Either[Stats, Exception]) -> str
        if isinstance(result, Right):
            value = result.value()
            return "%s %s %s" % (value.octal_mode(), value.user, value.group)
        elif isinstance(result, Left):
            return str(result.error())
        else:
            raise ValueError()

    result = StatReader().read_stats(path)
    return stats_str(result)


class Stats(NamedTuple('Result', [
    ('user', str),
    ('group', str),
    ('mode', int),
])):
    def octal_mode(self):  # () -> str
        return self._remove_octal_prefix(oct(self.mode & 0o777))

    @staticmethod
    def _remove_octal_prefix(mode):  # type: (str) -> str
        remove_new_octal_format = mode.replace('0o', '')
        remove_old_octal_format = re.sub(r"^0", '', remove_new_octal_format)
        return remove_old_octal_format


class StatReader:
    @staticmethod
    def read_stats(path,  # type: str
                   ):  # type: (...) -> Either[Stats, Exception]
        try:
            stats = os.lstat(path)
            user = getpwuid(stats.st_uid).pw_name
            group = getgrgid(stats.st_gid).gr_name
            mode = stats.st_mode

            return Right(Stats(user, group, mode))
        except (IOError, OSError) as e:
            return Left(e)
