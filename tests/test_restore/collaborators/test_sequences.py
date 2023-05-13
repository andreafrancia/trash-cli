import unittest

from trashcli.restore.restore_asking_the_user import parse_indexes


class TestSequences(unittest.TestCase):
    def test(self):
        sequences = parse_indexes("1-5,7", 10)
        result = [index for index in sequences.all_indexes()]
        self.assertEqual([1, 2, 3, 4, 5, 7], result)
