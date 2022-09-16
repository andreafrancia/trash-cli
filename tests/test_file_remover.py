import unittest

from trashcli.fs import FileRemover

try:
    FileNotFoundError  # python 2
except NameError:
    FileNotFoundError = IOError


class TestFileRemover(unittest.TestCase):
    def test_remove_file_fails_when_file_does_not_exists(self):
        file_remover = FileRemover()
        self.assertRaises(FileNotFoundError, file_remover.remove_file,
                          '/non/existing/path')
