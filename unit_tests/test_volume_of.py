from trashcli.fstab import VolumeOf
from trashcli.fstab import FakeIsMount
from nose.tools import assert_equals, istest
import os

@istest
class TestVolumeOf:

    def setUp(self):
        self.ismount = FakeIsMount()
        self.volume_of = VolumeOf(ismount = self.ismount)
        self.volume_of.abspath = os.path.normpath

    @istest
    def return_the_containing_volume(self):
        self.ismount.add_mount('/fake-vol')
        assert_equals('/fake-vol', self.volume_of('/fake-vol/foo'))

    @istest
    def with_file_that_are_outside(self):
        self.ismount.add_mount('/fake-vol')
        assert_equals('/', self.volume_of('/foo'))

    @istest
    def it_work_also_with_relative_mount_point(self):
        self.ismount.add_mount('relative-fake-vol')
        assert_equals('relative-fake-vol', self.volume_of('relative-fake-vol/foo'))

