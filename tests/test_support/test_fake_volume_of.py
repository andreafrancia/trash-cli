import pytest

from tests.support.fakes.fake_volume_of import FakeVolumeOf


class TestFakeVolumeOf:
    @pytest.fixture
    def volumes(self):
        return FakeVolumeOf()

    def test_return_the_containing_volume(self, volumes):
        volumes.add_volume('/fake-vol')

        assert '/fake-vol' == volumes.volume_of('/fake-vol/foo')

    def test_with_file_that_are_outside(self, volumes):
        volumes.add_volume('/fake-vol')

        assert '/' == volumes.volume_of('/foo')

    def test_it_work_also_with_relative_mount_point(self, volumes):
        volumes.add_volume('relative-fake-vol')

        assert 'relative-fake-vol' == volumes.volume_of(
            'relative-fake-vol/foo')
