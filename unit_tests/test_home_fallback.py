from mock import Mock, call, ANY

from trashcli.fstab import FakeFstab
from trashcli.put import GlobalTrashCan
from nose.tools import assert_equals

class TestHomeFallback:
    def setUp(self):
        self.reporter = Mock()
        mount_points = ['/', 'sandbox/other_partition']
        self.fs = Mock()
        self.trashcan = GlobalTrashCan(
                reporter = self.reporter,
                getuid = lambda: 123,
                volume_of = self.fake_volume_of(mount_points),
                now = None,
                environ = dict(),
                fs = self.fs)

    def test_should_skip_top_trash_if_does_not_exists(self):
        self.fs.mock_add_spec(['isdir', 'islink', 'move', 'atomic_write',
            'remove_file', 'ensure_dir'])
        self.fs.isdir.side_effect = lambda x:['.Trash'][False]
        self.fs.islink.side_effect = lambda x:['.Trash'][False]

        self.trashcan.trash('sandbox/foo')

        assert_equals([
            call.isdir('.Trash'),
            call.islink('.Trash'),
            call.ensure_dir('.Trash/123/info', 448),
            call.atomic_write('.Trash/123/info/foo.trashinfo', ANY),
            call.ensure_dir('.Trash/123/files', 448),
            call.move('sandbox/foo', '.Trash/123/files/foo')
        ], self.fs.mock_calls)

    def fake_volume_of(self, volumes):
        fstab = FakeFstab()
        for vol in volumes:
            fstab.add_mount(vol)
        return fstab.volume_of

from trashcli.trash import TrashDirectories
from trashcli.restore import AllTrashDirectories
class TestTrashDirectories:
    def test_list_all_directories(self):
        self.volume_of = Mock()
        self.getuid = lambda:123
        self.mount_points = ['/', '/mnt']
        self.environ = {'HOME': '~'}
        trash_dirs = TrashDirectories(
                volume_of    = self.volume_of,
                getuid       = self.getuid,
                environ      = self.environ)
        all_trash_directories = AllTrashDirectories()

        result = all_trash_directories.all_trash_directories(trash_dirs, self.mount_points)
        paths = map(lambda td: td.path, result)

        assert_equals( ['~/.local/share/Trash',
                        '/.Trash/123',
                        '/.Trash-123',
                        '/mnt/.Trash/123',
                        '/mnt/.Trash-123'] , paths)

