from trashcli.trash import VolumeOf
from trashcli.trash import FakeIsMount
from nose.tools import assert_equals, istest, assert_not_equals

class TestVolumeOf:
    @istest
    def can_be_configured(self):
        ismount = FakeIsMount()
        ismount.add_mount('/fake-vol')
        volume_of = VolumeOf(ismount = ismount)

        assert_equals('/', volume_of('/foo'))
        assert_equals('/fake-vol', volume_of('/fake-vol/foo'))

    @istest
    def should_handle_relative_mounts(self):
        ismount = FakeIsMount()
        ismount.add_mount('rel-vol')
        volume_of = VolumeOf(ismount = ismount)

        #TODO: should be equal instead!
        assert_not_equals('rel-vol', volume_of('rel-vol/foo'))

