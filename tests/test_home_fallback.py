import unittest

from mock import Mock, call, ANY

from trashcli.fstab import create_fake_volume_of
from trashcli.put import TrashPutCmd
from datetime import datetime
import os


class TestHomeFallback(unittest.TestCase):
    def setUp(self):
        self.reporter = Mock()
        mount_points = ['/', 'sandbox/other_partition']
        self.fs = Mock()
        self.trashcan = TrashPutCmd(
                stdout=None,
                stderr=None,
                getuid = lambda: 123,
                volumes = create_fake_volume_of(mount_points),
                now = datetime.now,
                environ = dict(),
                fs = self.fs,
                parent_path = os.path.dirname,
                realpath = lambda x:x)
        self.trashcan.reporter = self.reporter
        self.trashcan.logger = Mock()
        self.trashcan.ignore_missing = False

    def test_use_of_top_trash_dir_when_sticky(self):
        self.fs.mock_add_spec(['isdir', 'islink', 'has_sticky_bit',
                               'move', 'atomic_write',
                               'remove_file', 'ensure_dir'])
        self.fs.isdir.return_value = True
        self.fs.islink.return_value = False
        self.fs.has_sticky_bit.return_value = True

        self.trashcan.trash('sandbox/foo', False)

        assert [
            call.isdir('.Trash'),
            call.islink('.Trash'),
            call.has_sticky_bit('.Trash'),
            call.ensure_dir('.Trash/123/info', 448),
            call.atomic_write('.Trash/123/info/foo.trashinfo', ANY),
            call.ensure_dir('.Trash/123/files', 448),
            call.move('sandbox/foo', '.Trash/123/files/foo')
        ] == self.fs.mock_calls

    def test_bug_will_use_top_trashdir_even_with_not_sticky(self):
        self.fs.mock_add_spec(['isdir', 'islink', 'has_sticky_bit',
                               'move', 'atomic_write',
                               'remove_file', 'ensure_dir'])
        self.fs.isdir.return_value = True
        self.fs.islink.return_value = False
        self.fs.has_sticky_bit.return_value = False

        self.trashcan.trash('sandbox/foo', False)

        assert [
            call.isdir('.Trash'),
            call.islink('.Trash'),
            call.has_sticky_bit('.Trash'),
            call.ensure_dir('.Trash-123/info', 448),
            call.atomic_write('.Trash-123/info/foo.trashinfo', ANY),
            call.ensure_dir('.Trash-123/files', 448),
            call.move('sandbox/foo', '.Trash-123/files/foo')
        ] == self.fs.mock_calls, self.fs.mock_calls
