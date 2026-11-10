import os
import unittest

import pytest

from trashcli.fslib.fs_remove_file_if_exists import FsRemoveFileIfExists
from trashcli.fslib.real.real_fs import RealFs


@pytest.mark.slow
class TestFsRemoveFileIfExists(unittest.TestCase):

    def test_remove_file_if_exists__does_not_fail___when_file_does_not_exists(self):
        file_remover = FsRemoveFileIfExists(RealFs(), {}, os.geteuid)
        file_remover.remove_file_if_exists('/non/existing/path')
