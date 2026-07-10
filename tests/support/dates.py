import datetime

from tests.support.trashinfo.parse_date import parse_date


def jan_11_2001():  # type: (...) -> datetime.datetime
    return parse_date("2001-01-01")
