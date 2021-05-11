import unittest
import datetime


def version_from_date(today):
    return "0.%s.%s.%s" % (today.year % 100,
                           today.month,
                           today.day)


class TestBump(unittest.TestCase):
    def test(self):
        today = datetime.date(2021, 5, 11)
        result = version_from_date(today)

        assert result == '0.21.5.11'
