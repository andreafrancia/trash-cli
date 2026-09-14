import datetime

from tests.support.tools.version_from_date import dev_version_from_date
from tests.support.tools.version_from_date import sanitize_local_version_label
from tests.support.tools.version_from_date import version_from_date


class TestVersionFromDate:
    def test(self):
        today = datetime.date(2021, 5, 11)
        result = version_from_date(today)

        assert result == '0.21.5.11'


class TestSanitizeLocalVersionLabel:
    def test_replaces_hyphens_with_dots(self):
        assert sanitize_local_version_label('fix-build-failure-27') == \
               'fix.build.failure.27'

    def test_collapses_consecutive_separators_into_one_dot(self):
        assert sanitize_local_version_label('a--b__c..d') == 'a.b.c.d'


class TestDevVersionFromDate:
    def test_sanitizes_hyphens_in_ref(self):
        today = datetime.date(2021, 5, 11)
        result = dev_version_from_date('fix-build-failure-27', 'abc123', today)

        assert result == '0.21.5.11.dev0+git.fix.build.failure.27.abc123'


