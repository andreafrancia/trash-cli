import unittest

import six

from trashcli.restore.range import Range
from trashcli.restore.restore_asking_the_user import InvalidEntry, parse_indexes
from trashcli.restore.sequences import Sequences
from trashcli.restore.single import Single


class TestParseIndexes(unittest.TestCase):
    def test_non_numeric(self):
        with six.assertRaisesRegex(self, InvalidEntry, "^not an index: a$"):
            parse_indexes("a", 10)

    def test(self):
        with six.assertRaisesRegex(self, InvalidEntry, "^out of range 0..9: 10$"):
            parse_indexes("10", 10)

    def test2(self):
        self.assertEqual(Sequences([Single(9)]), parse_indexes("9", 10))

    def test3(self):
        self.assertEqual(Sequences([Single(0)]), parse_indexes("0", 10))

    def test4(self):
        assert Sequences([Range(1, 4)]) == parse_indexes("1-4", 10)

    def test5(self):
        self.assertEqual(Sequences([Single(1),
                                    Single(2),
                                    Single(3),
                                    Single(4)]),
                         parse_indexes("1,2,3,4", 10))

    def test_interval_without_start(self):
        with six.assertRaisesRegex(self, InvalidEntry, "^open interval: -1$"):
            parse_indexes("-1", 10)

    def test_interval_without_end(self):
        with six.assertRaisesRegex(self, InvalidEntry, "^open interval: 1-$"):
            parse_indexes("1-", 10)

    def test_complex(self):
        indexes = parse_indexes("1-5,7", 10)
        self.assertEqual(Sequences([Range(1, 5), Single(7)]), indexes)
