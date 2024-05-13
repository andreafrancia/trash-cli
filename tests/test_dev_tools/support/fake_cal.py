from tests.support.tools.core.cal import Cal
from tests.support.trashinfo.parse_date import parse_date


class FakeCal(Cal):
    def __init__(self, today):
        self._today = parse_date(today)

    def today(self):
        return self._today

