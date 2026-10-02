import unittest

from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.fslib.real.real_fs import RealFs


class TestExistingFileRemover(unittest.TestCase):

    def test_remove_file_if_exists_fails_when_file_does_not_exists(self):
        file_remover = ExistingFileRemover(RealFs())
        file_remover.remove_file_if_exists('/non/existing/path')
