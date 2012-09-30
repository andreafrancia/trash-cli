import os

from mock import Mock

from trashcli.fstab import FakeFstab
from trashcli.put import GlobalTrashCan
from nose.tools import assert_equals

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

from trashcli.trash import TrashDirectories
class TestTrashDirectories:
    def test_list_all_directories(self):
        self.volume_of = Mock()
        self.getuid = lambda:123
        self.mount_points = ['/', '/mnt']
        self.environ = {'HOME': '~'}
        trash_dirs = TrashDirectories(
                volume_of    = self.volume_of,
                getuid       = self.getuid,
                mount_points = self.mount_points,
                environ      = self.environ)

        result = trash_dirs.all_trash_directories()
        paths = map(lambda td: td.path, result)

        assert_equals( ['~/.local/share/Trash',
                        '/.Trash/123',
                        '/.Trash-123',
                        '/mnt/.Trash/123',
                        '/mnt/.Trash-123'] , paths)
