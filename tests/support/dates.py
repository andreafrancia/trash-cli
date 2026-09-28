import datetime

from tests.support.trashinfo.parse_date import parse_date


def jan_11_2001():  # type: (...) -> datetime.datetime
    return parse_date("2001-01-01")

def date_at(year, month, day):
    return datetime.datetime(year, month, day, 0, 0)
