from trashcli.fstab import FakeIsMount

from nose.tools import istest
from nose.tools import assert_false
from nose.tools import assert_true

@istest
class OnDefault:
    def setUp(self):
        self.ismount = FakeIsMount()

    @istest
    def by_default_root_is_mount(self):

        assert_true(self.ismount('/'))

    @istest
    def while_by_default_any_other_is_not_a_mount_point(self):

        assert_false(self.ismount('/any/other'))

@istest
class WhenOneFakeVolumeIsDefined:
    def setUp(self):
        self.ismount = FakeIsMount()
        self.ismount.add_mount('/fake-vol')

    @istest
    def accept_fake_mount_point(self):

        assert_true(self.ismount('/fake-vol'))

    @istest
    def other_still_are_not_mounts(self):

        assert_false(self.ismount('/other'))

    @istest
    def dont_get_confused_by_traling_slash(self):

        assert_true(self.ismount('/fake-vol/'))

@istest
class WhenMultipleFakesMountPoints:
    def setUp(self):
        self.ismount = FakeIsMount()
        self.ismount.add_mount('/vol1')
        self.ismount.add_mount('/vol2')

    @istest
    def recognize_both(self):
        assert_true(self.ismount('/vol1'))
        assert_true(self.ismount('/vol2'))
        assert_false(self.ismount('/other'))

@istest
def should_handle_relative_volumes():
    ismount = FakeIsMount()
    ismount.add_mount('fake-vol')
    assert_true(ismount('fake-vol'))
