import datetime

from trashcli.restore.args import Sort
from trashcli.restore.sort_method import sort_files
from trashcli.restore.trashed_file import TrashedFile


def a_file(location, date):
    return TrashedFile(location, date, '/info', '/original')


jan = datetime.datetime(2020, 1, 1)
feb = datetime.datetime(2020, 2, 1)


class TestSortMethod:
    def test_do_not_sort_keeps_the_original_order(self):
        files = [a_file('/b', feb), a_file('/a', jan)]

        result = list(sort_files(Sort.DoNot, files))

        assert [f.original_location for f in result] == ['/b', '/a']

    def test_do_not_sort_returns_a_reusable_sequence(self):
        # the real caller passes a generator, then len()s and re-iterates it
        def gen():
            yield a_file('/b', feb)
            yield a_file('/a', jan)

        result = sort_files(Sort.DoNot, gen())

        assert len(result) == 2
        assert [f.original_location for f in result] == ['/b', '/a']

    def test_sort_by_date(self):
        files = [a_file('/b', feb), a_file('/a', jan)]

        result = list(sort_files(Sort.ByDate, files))

        assert [f.original_location for f in result] == ['/a', '/b']

    def test_sort_by_date_tolerates_a_missing_date(self):
        # a None (unparsable) date must not blow up the comparison; sorts first
        files = [a_file('/dated', jan), a_file('/undated', None)]

        result = list(sort_files(Sort.ByDate, files))

        assert [f.original_location for f in result] == ['/undated', '/dated']

    def test_sort_by_path_tolerates_a_missing_date(self):
        files = [a_file('/b', None), a_file('/a', None)]

        result = list(sort_files(Sort.ByPath, files))

        assert [f.original_location for f in result] == ['/a', '/b']
