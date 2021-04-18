import unittest

from trashcli.fstab import VolumeOf
from trashcli.fstab import FakeIsMount
import os


class TestVolumeOf(unittest.TestCase):

    def test_return_the_containing_volume(self):
        self.ismount = FakeIsMount(['/fake-vol'])
        self.volume_of = VolumeOf(self.ismount, os.path.normpath)

        assert '/fake-vol' == self.volume_of('/fake-vol/foo')

    def test_with_file_that_are_outside(self):
        self.ismount = FakeIsMount(['/fake-vol'])
        self.volume_of = VolumeOf(self.ismount, os.path.normpath)

        assert '/' == self.volume_of('/foo')

    def test_it_work_also_with_relative_mount_point(self):
        self.ismount = FakeIsMount(['relative-fake-vol'])
        self.volume_of = VolumeOf(self.ismount, os.path.normpath)

        assert 'relative-fake-vol' == self.volume_of('relative-fake-vol/foo')
