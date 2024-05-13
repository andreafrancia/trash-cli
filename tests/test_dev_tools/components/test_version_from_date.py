import datetime

from tests.support.tools.version_from_date import version_from_date


class TestVersionFromDate:
    def test(self):
        today = datetime.date(2021, 5, 11)
        result = version_from_date(today)

        assert result == '0.21.5.11'


