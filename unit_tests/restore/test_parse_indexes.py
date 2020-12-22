import unittest

import six

from trashcli.restore import parse_indexes, InvalidEntry


class Test_parse_indexes(unittest.TestCase):
    def test_non_numeric(self):
        with six.assertRaisesRegex(self, InvalidEntry, "^not an index: a$"):
            parse_indexes("a", 10)

    def test(self):
        with six.assertRaisesRegex(self, InvalidEntry, "^out of range 0..9: 10$"):
            parse_indexes("10", 10)

    def test2(self):
        self.assertEqual([9], parse_indexes("9", 10))

    def test3(self):
        self.assertEqual([0], parse_indexes("0", 10))

    def test4(self):
        with six.assertRaisesRegex(self, InvalidEntry, 'out of range 0..9: -1'):
            parse_indexes("-1", 10)

    def test5(self):
        self.assertEqual([4, 3, 2, 1], parse_indexes("1,2,3,4", 10))
