import os

from mock import Mock

from trashcli.fstab import FakeFstab
from trashcli.put import GlobalTrashCan


class TestHomeFallback:
    def test_should_use_home_trash_as_fallback(self):
        reporter = Mock()
        mount_points = ['/', 'sandbox/other_partition']
        self.having_file('sandbox/other_partition/foo')
        out = Mock()
        self.trashcan = GlobalTrashCan(
                reporter = reporter,
                getuid = lambda: 123,
                fstab = self.fake_volume_of(mount_points),
                now = None,
                environ = dict(),
                )
        self.trashcan._trash_file_in_directory = out

        self.trashcan.trash('sandbox/foo')



    def having_file(self, path):
        os.makedirs(os.path.dirname(path))
        file(path, 'w' ).write('')
    def fake_volume_of(self, volumes):
        fstab = FakeFstab()
        for vol in volumes:
            fstab.add_mount(vol)
        return fstab
