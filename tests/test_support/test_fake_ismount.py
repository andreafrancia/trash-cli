import unittest

from tests.support.fake_is_mount import FakeIsMount


class TestOnDefault(unittest.TestCase):
    def setUp(self):
        self.ismount = FakeIsMount([])

    def test_by_default_root_is_mount(self):

        assert self.ismount.is_mount('/')

    def test_while_by_default_any_other_is_not_a_mount_point(self):

        assert not self.ismount.is_mount('/any/other')

class WhenOneFakeVolumeIsDefined(unittest.TestCase):
    def setUp(self):
        self.ismount = FakeIsMount(['/fake-vol'])

    def test_accept_fake_mount_point(self):

        assert self.ismount.is_mount('/fake-vol')

    def test_other_still_are_not_mounts(self):

        assert not self.ismount.is_mount('/other')

    def test_dont_get_confused_by_traling_slash(self):

        assert self.ismount.is_mount('/fake-vol/')


class TestWhenMultipleFakesMountPoints(unittest.TestCase):
    def setUp(self):
        self.ismount = FakeIsMount(['/vol1', '/vol2'])

    def test_recognize_both(self):
        assert self.ismount.is_mount('/vol1')
        assert self.ismount.is_mount('/vol2')
        assert not self.ismount.is_mount('/other')


def test_should_handle_relative_volumes():
    ismount = FakeIsMount(['fake-vol'])
    assert ismount.is_mount('fake-vol')
