import unittest

from trashcli.rm.real_remover_fs import RealRemoverFs


try:
    FileNotFoundError
except NameError:
    FileNotFoundError = OSError  # python 2


class TestFileRemover(unittest.TestCase):
    def test_remove_file_fails_when_file_does_not_exists(self):
        file_remover = RealRemoverFs()
        self.assertRaises(FileNotFoundError, file_remover.remove_file2,
                          '/non/existing/path')
