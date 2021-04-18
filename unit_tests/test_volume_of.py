import unittest

from trashcli.fstab import Volumes
from trashcli.fstab import FakeIsMount
import os


class TestVolumeOf(unittest.TestCase):

    def test_return_the_containing_volume(self):
        ismount = FakeIsMount(['/fake-vol'])
        self.volumes = Volumes(ismount, os.path.normpath)

        assert '/fake-vol' == self.volumes.volume_of('/fake-vol/foo')

    def test_with_file_that_are_outside(self):
        ismount = FakeIsMount(['/fake-vol'])
        self.volumes = Volumes(ismount, os.path.normpath)

        assert '/' == self.volumes.volume_of('/foo')

    def test_it_work_also_with_relative_mount_point(self):
        ismount = FakeIsMount(['relative-fake-vol'])
        self.volumes = Volumes(ismount, os.path.normpath)

        assert 'relative-fake-vol' == self.volumes.volume_of('relative-fake-vol/foo')
