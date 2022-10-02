import datetime


class PutClock:
    def now(self):  # type: () -> datetime.datetime
        raise NotImplementedError()


class RealClock(PutClock):
    def now(self):  # type: () -> datetime.datetime
        return datetime.datetime.now()
