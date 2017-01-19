from mock import Mock, call, ANY

from trashcli.fstab import FakeFstab
from trashcli.put import GlobalTrashCan
from nose.tools import assert_equals
from datetime import datetime
import os

class TestHomeFallback:
    def setUp(self):
        self.reporter = Mock()
        mount_points = ['/', 'sandbox/other_partition']
        self.fs = Mock()
        self.trashcan = GlobalTrashCan(
                reporter = self.reporter,
                getuid = lambda: 123,
                volume_of = self.fake_volume_of(mount_points),
                now = datetime.now,
                environ = dict(),
                fs = self.fs,
                parent_path = os.path.dirname,
                realpath = lambda x:x,
                logger = Mock())

    def test_use_of_top_trash_dir_when_sticky(self):
        self.fs.mock_add_spec(['isdir', 'islink', 'has_sticky_bit',
                               'move', 'atomic_write',
                               'remove_file', 'ensure_dir'])
        self.fs.isdir.return_value = True
        self.fs.islink.return_value = False
        self.fs.has_sticky_bit.return_value = True

        self.trashcan.trash('sandbox/foo')

        assert_equals([
            call.isdir('.Trash'),
            call.islink('.Trash'),
            call.has_sticky_bit('.Trash'),
            call.ensure_dir('.Trash/123/info', 448),
            call.atomic_write('.Trash/123/info/foo.trashinfo', ANY),
            call.ensure_dir('.Trash/123/files', 448),
            call.move('sandbox/foo', '.Trash/123/files/foo')
        ], self.fs.mock_calls)

    def test_bug_will_use_top_trashdir_even_with_not_sticky(self):
        self.fs.mock_add_spec(['isdir', 'islink', 'has_sticky_bit',
                               'move', 'atomic_write',
                               'remove_file', 'ensure_dir'])
        self.fs.isdir.return_value = True
        self.fs.islink.return_value = False
        self.fs.has_sticky_bit.return_value = False

        self.trashcan.trash('sandbox/foo')

        assert_equals([
            call.isdir('.Trash'),
            call.islink('.Trash'),
            call.has_sticky_bit('.Trash'),
            call.ensure_dir('.Trash-123/info', 448),
            call.atomic_write('.Trash-123/info/foo.trashinfo', ANY),
            call.ensure_dir('.Trash-123/files', 448),
            call.move('sandbox/foo', '.Trash-123/files/foo')
        ], self.fs.mock_calls, self.fs.mock_calls)

    def fake_volume_of(self, volumes):
        fstab = FakeFstab()
        for vol in volumes:
            fstab.add_mount(vol)
        return fstab.volume_of

from trashcli.trash import TrashDirectories
from trashcli.restore import AllTrashDirectories
class TestTrashDirectories:
    def test_list_all_directories(self):
        all_trash_directories = AllTrashDirectories(
                volume_of    = Mock(),
                getuid       = lambda:123,
                environ      = {'HOME': '~'},
                mount_points = ['/', '/mnt'])

        result = all_trash_directories.all_trash_directories()
        paths = list(map(lambda td: td.path, result))

        assert_equals( ['~/.local/share/Trash',
                        '/.Trash/123',
                        '/.Trash-123',
                        '/mnt/.Trash/123',
                        '/mnt/.Trash-123'] , paths)

