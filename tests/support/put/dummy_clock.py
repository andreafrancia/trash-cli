import datetime

from trashcli.put.clock import PutClock


class FixedClock(PutClock):
    def __init__(self, now_value=None):
        self.now_value = now_value

    def set_clock(self, now_value):
        self.now_value = now_value

    def now(self):  # type: () -> datetime.datetime
        return self.now_value

    @staticmethod
    def fixet_at_jan_1st_2024():
        return FixedClock(now_value=jan_1st_2024())

def jan_1st_2024():
    return datetime.datetime(2014, 1, 1, 0, 0, 0)
