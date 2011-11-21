from nose.tools import assert_equals
import unittest

from trashcli.trash import GlobalTrashCan

class GlobalTrashCanTest(unittest.TestCase):
    def test_something(self):
        assert_equals(1,1)

    def test_fixture(self):
        def do_nothing(info_path, path): pass
        a=GlobalTrashCan()
        a.for_all_trashed_file(do_nothing)

