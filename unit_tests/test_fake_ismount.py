import unittest

from trashcli.fstab import FakeIsMount

class TestOnDefault(unittest.TestCase):
    def setUp(self):
        self.ismount = FakeIsMount()

    def test_by_default_root_is_mount(self):

        assert self.ismount('/')

    def test_while_by_default_any_other_is_not_a_mount_point(self):

        assert not self.ismount('/any/other')

class WhenOneFakeVolumeIsDefined(unittest.TestCase):
    def setUp(self):
        self.ismount = FakeIsMount()
        self.ismount.add_mount('/fake-vol')

    def test_accept_fake_mount_point(self):

        assert self.ismount('/fake-vol')

    def test_other_still_are_not_mounts(self):

        assert not self.ismount('/other')

    def test_dont_get_confused_by_traling_slash(self):

        assert self.ismount('/fake-vol/')


class TestWhenMultipleFakesMountPoints(unittest.TestCase):
    def setUp(self):
        self.ismount = FakeIsMount()
        self.ismount.add_mount('/vol1')
        self.ismount.add_mount('/vol2')

    def test_recognize_both(self):
        assert self.ismount('/vol1')
        assert self.ismount('/vol2')
        assert not self.ismount('/other')


def test_should_handle_relative_volumes():
    ismount = FakeIsMount()
    ismount.add_mount('fake-vol')
    assert ismount('fake-vol')
