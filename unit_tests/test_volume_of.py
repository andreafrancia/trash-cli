import unittest

from trashcli.fstab import VolumeOf
from trashcli.fstab import FakeIsMount
from unit_tests.tools import assert_equal
import os


class TestVolumeOf(unittest.TestCase):

    def setUp(self):
        self.ismount = FakeIsMount()
        self.volume_of = VolumeOf(self.ismount, os.path.normpath)

    def test_return_the_containing_volume(self):
        self.ismount.add_mount('/fake-vol')
        assert_equal('/fake-vol', self.volume_of('/fake-vol/foo'))

    def test_with_file_that_are_outside(self):
        self.ismount.add_mount('/fake-vol')
        assert_equal('/', self.volume_of('/foo'))

    def test_it_work_also_with_relative_mount_point(self):
        self.ismount.add_mount('relative-fake-vol')
        assert_equal('relative-fake-vol', self.volume_of('relative-fake-vol/foo'))
