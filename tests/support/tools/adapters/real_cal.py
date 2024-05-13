import datetime

from tests.support.tools.core.cal import Cal


class RealCal(Cal):
    def today(self):
        return datetime.datetime.today()
