import collections
import os
import unittest

from tests.support.dirs.my_path import MyPath
from tests.support.py2mock import patch
from trashcli.restore.file_system import FileReader
from trashcli.restore.trashed_files import TrashedFiles


InfoFile = collections.namedtuple('InfoFile', 'path type volume')


class FakeReader(FileReader):
    def contents_of(self, path):
        return open(path).read()


class FakeSearcher:
    def __init__(self, info_dir):
        self.info_dir = info_dir

    def all_file_in_info_dir(self, trash_dir_from_cli):
        for name in sorted(os.listdir(self.info_dir)):
            yield InfoFile(os.path.join(self.info_dir, name), 'trashinfo', '/')


class MemoLogger:
    def __init__(self):
        self.messages = []

    def warning(self, msg):
        self.messages.append(msg)


class TestRestoreOwnerCheck(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()

    def _trashed_files_in(self, mode):
        info_dir = self.tmp_dir / ('trash-%o' % mode) / 'info'
        os.makedirs(info_dir)
        os.chmod(info_dir, mode)
        with open(info_dir / 'x.trashinfo', 'w') as f:
            f.write('[Trash Info]\nPath=/foo/x\n'
                    'DeletionDate=2000-01-01T00:00:00\n')
        return TrashedFiles(MemoLogger(), FakeReader(), FakeSearcher(info_dir))

    def _restorable(self, trashed_files):
        return [os.path.basename(tf.info_file)
                for tf in trashed_files.all_trashed_files(None)]

    def test_foreign_owned_entry_is_hidden_in_a_world_writable_dir(self):
        trashed_files = self._trashed_files_in(0o1777)

        # pretend we run as a user who does not own the (root-owned) trashinfo
        with patch('os.geteuid', return_value=os.getuid() + 4242):
            self.assertEqual([], self._restorable(trashed_files))

    def test_foreign_owned_entry_is_kept_in_a_private_dir(self):
        trashed_files = self._trashed_files_in(0o700)

        with patch('os.geteuid', return_value=os.getuid() + 4242):
            self.assertEqual(['x.trashinfo'], self._restorable(trashed_files))

    def tearDown(self):
        self.tmp_dir.clean_up()
