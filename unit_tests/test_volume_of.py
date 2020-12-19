import unittest

from trashcli.fstab import VolumeOf
from trashcli.fstab import FakeIsMount
import os


class TestVolumeOf(unittest.TestCase):

    def setUp(self):
        self.ismount = FakeIsMount()
        self.volume_of = VolumeOf(self.ismount, os.path.normpath)

    def test_return_the_containing_volume(self):
        self.ismount.add_mount('/fake-vol')
        assert '/fake-vol' == self.volume_of('/fake-vol/foo')

    def test_with_file_that_are_outside(self):
        self.ismount.add_mount('/fake-vol')
        assert '/' == self.volume_of('/foo')

    def test_it_work_also_with_relative_mount_point(self):
        self.ismount.add_mount('relative-fake-vol')
        assert 'relative-fake-vol' == self.volume_of('relative-fake-vol/foo')
