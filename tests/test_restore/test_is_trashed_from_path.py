import unittest

from trashcli.restore.restore_cmd import original_location_matches_path


class Test_original_location_matches_path(unittest.TestCase):
    def test1(self):
        assert original_location_matches_path("/full/path", "/full") == True

    def test2(self):
        assert original_location_matches_path("/full/path", "/full/path") == True

    def test3(self):
        assert original_location_matches_path("/prefix-extension", "/prefix") == False

    def test_root(self):
        assert original_location_matches_path("/any/path", "/") == True
