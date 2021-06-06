import datetime
import unittest
from trashcli.trash import Clock
from mock import Mock


class TestClock(unittest.TestCase):
    def setUp(self):
        self.errors = Mock(spec=[])

    def test_return_real_time(self):
        assert Clock(lambda: 'now', {}).get_now_value(self.errors) == 'now'

    def test_return_fake_time(self):
        clock = Clock(lambda: 'now',
                      {'TRASH_DATE': '2021-06-04T18:40:19'})

        assert clock.get_now_value(self.errors) == datetime.datetime(2021, 6, 4, 18, 40, 19)
