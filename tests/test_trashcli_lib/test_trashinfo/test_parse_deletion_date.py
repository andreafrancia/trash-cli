from datetime import datetime

from trashcli.parse_trashinfo.parse_deletion_date import parse_deletion_date


class TestParseDeletionDate:
    def test1(self):
        assert parse_deletion_date('DeletionDate=2000-12-31T23:59:58') == \
               datetime(2000, 12, 31, 23, 59, 58)

    def test2(self):
        assert parse_deletion_date('DeletionDate=2000-12-31T23:59:58\n') == \
               datetime(2000, 12, 31, 23, 59, 58)

    def test3(self):
        assert parse_deletion_date(
            '[Trash Info]\nDeletionDate=2000-12-31T23:59:58') == \
               datetime(2000, 12, 31, 23, 59, 58)

    def test_two_deletion_dates(self):
        assert parse_deletion_date('DeletionDate=2000-01-01T00:00:00\n'
                                   'DeletionDate=2000-12-31T00:00:00\n') == \
               datetime(2000, 1, 1, 0, 0)
