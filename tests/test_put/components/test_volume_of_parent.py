import unittest
from typing import cast

import flexmock

from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.fstab.volume_of import VolumeOf
from trashcli.put.fs.parent_realpath import ParentRealpathFs
from trashcli.put.fs.volume_of_parent import VolumeOfParent


class TestVolumeOfParent(unittest.TestCase):
    def setUp(self):
        self.fs = FakeFs()

        self.volume_of_parent = VolumeOfParent(self.fs)

    def test(self):
        self.fs.add_volume('/path')

        result = self.volume_of_parent.volume_of_parent('/path/to/file')

        assert result == '/path'
