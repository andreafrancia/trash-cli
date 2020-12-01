from trashcli.fstab import VolumeOf
from trashcli.fstab import FakeIsMount
from nose.tools import assert_equal, istest
import os

@istest
class TestVolumeOf:

    def setUp(self):
        self.ismount = FakeIsMount()
        self.volume_of = VolumeOf(self.ismount, os.path.normpath)

    @istest
    def return_the_containing_volume(self):
        self.ismount.add_mount('/fake-vol')
        assert_equal('/fake-vol', self.volume_of('/fake-vol/foo'))

    @istest
    def with_file_that_are_outside(self):
        self.ismount.add_mount('/fake-vol')
        assert_equal('/', self.volume_of('/foo'))

    @istest
    def it_work_also_with_relative_mount_point(self):
        self.ismount.add_mount('relative-fake-vol')
        assert_equal('relative-fake-vol', self.volume_of('relative-fake-vol/foo'))

