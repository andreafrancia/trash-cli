import datetime

from trashcli.put.clock import PutClock


class DummyClock(PutClock):
    def __init__(self, now_value=None):
        self.now_value = now_value

    def set_clock(self, now_value):
        self.now_value = now_value

    def now(self):  # type: () -> datetime.datetime
        return self.now_value
