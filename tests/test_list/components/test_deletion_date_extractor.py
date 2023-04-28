import datetime
import unittest

from trashcli.list.extractors import DeletionDateExtractor


class TestDeletionDateExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = DeletionDateExtractor()

    def test_extract_attribute_default(self):
        result = self.extractor.extract_attribute(None, "DeletionDate=")
        assert result == '????-??-?? ??:??:??'

    def test_extract_attribute_value(self):
        result = self.extractor.extract_attribute(None, "DeletionDate=2001-01-01T10:10:10")
        assert result == datetime.datetime(2001, 1, 1, 10, 10, 10)
