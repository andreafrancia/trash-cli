import datetime
import unittest
from trashcli.trash import Clock


class TestClock(unittest.TestCase):
    def test_return_real_time(self):
        assert Clock(lambda: 'now', {}).get_now_value() == 'now'

    def test_return_fake_time(self):
        clock = Clock(lambda: 'now',
                      {'TRASH_DATE': '2021-06-04T18:40:19'})

        assert clock.get_now_value() == datetime.datetime(2021, 6, 4, 18, 40, 19)
