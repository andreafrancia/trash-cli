from tests.support.trashinfo.trashinfos import \
    a_trashinfo_without_deletion_date, make_trashinfo
from trashcli.parse_trashinfo.maybe_parse_deletion_date import unknown_date, maybe_parse_deletion_date


class TestMaybeParseDeletionDate:
    def test_on_trashinfo_without_date_parse_to_unknown_date(self):
        assert (unknown_date ==
                maybe_parse_deletion_date(a_trashinfo_without_deletion_date()))

    def test_on_trashinfo_with_date_parse_to_date(self):
        from datetime import datetime
        example_date_as_string = '2001-01-01T00:00:00'
        same_date_as_datetime = datetime(2001, 1, 1)
        assert (same_date_as_datetime ==
                maybe_parse_deletion_date(
                    make_trashinfo(example_date_as_string)))

    def test_on_trashinfo_with_invalid_date_parse_to_unknown_date(self):
        invalid_date = 'A long time ago'
        assert (unknown_date ==
                maybe_parse_deletion_date(make_trashinfo(invalid_date)))
