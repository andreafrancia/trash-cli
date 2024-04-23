from datetime import datetime


def parse_date(date_string,  # type: str
               ):  # type: (...) -> datetime
    for format in ['%Y-%m-%d',
                   '%Y-%m-%dT%H:%M:%S',
                   '%Y-%m-%d %H:%M:%S',
                   ]:
        try:
            return datetime.strptime(date_string, format)
        except ValueError:
            continue
    raise ValueError("Can't parse date: %s" % date_string)
