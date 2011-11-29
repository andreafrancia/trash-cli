from nose.tools import assert_equals
from trashcli.trash2 import read_deletion_date

def test_how_to_parse_date_from_trashinfo():
    from datetime import datetime
    assert_equals(datetime(2000,12,31,23,59,58), read_deletion_date('DeletionDate=2000-12-31T23:59:58'))
    assert_equals(datetime(2000,12,31,23,59,58), read_deletion_date('DeletionDate=2000-12-31T23:59:58\n'))
    assert_equals(datetime(2000,12,31,23,59,58), read_deletion_date('[TrashInfo]\nDeletionDate=2000-12-31T23:59:58'))

from trashcli.trash2 import read_path

def test_how_to_parse_original_path():
    assert_equals('foo.txt', read_path('Path=foo.txt'))
    assert_equals('/path/to/be/escaped', read_path('Path=%2Fpath%2Fto%2Fbe%2Fescaped'))

from trashcli.trash2 import TrashInfoParser
import fudge

class TestTrashinfoParser:
    def setUp(self):
        fudge.clear_calls()
        fudge.clear_expectations()

        self.errors = fudge.Fake('error')

        self.parser = TrashInfoParser(self.errors)

    def test_it_signals_both_the_problem(self):
        
        self.errors.expects('unparsable_path')
        self.errors.expects('unparsable_deletion_date')

        self.parser.parse("")

    def test_when_no_path(self):

        self.errors.expects('unparsable_path')

        self.parser.parse('DeletionDate=2000-12-31T23:59:58')

    def tearDown(self):
        fudge.verify()
