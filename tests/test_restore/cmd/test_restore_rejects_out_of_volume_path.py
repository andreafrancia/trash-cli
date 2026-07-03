import collections
import os
import unittest

from tests.support.dirs.my_path import MyPath
from trashcli.restore.file_system import FileReader
from trashcli.restore.trashed_files import TrashedFiles


InfoFile = collections.namedtuple('InfoFile', 'path type volume')


class FakeReader(FileReader):
    def contents_of(self, path):
        return open(path).read()


class FakeSearcher:
    def __init__(self, info_dir, volume):
        self.info_dir = info_dir
        self.volume = volume

    def all_file_in_info_dir(self, trash_dir_from_cli):
        for name in sorted(os.listdir(self.info_dir)):
            yield InfoFile(os.path.join(self.info_dir, name), 'trashinfo',
                           self.volume)


class MemoLogger:
    def __init__(self):
        self.messages = []

    def warning(self, msg):
        self.messages.append(msg)


class TestRestoreRejectsOutOfVolumePath(unittest.TestCase):
    def setUp(self):
        self.volume = MyPath.make_temp_dir()
        self.info_dir = self.volume / '.Trash-1000' / 'info'
        os.makedirs(self.info_dir)
        self.logger = MemoLogger()
        self.trashed_files = TrashedFiles(self.logger, FakeReader(),
                                          FakeSearcher(self.info_dir,
                                                       self.volume))

    def _add(self, name, path_line):
        with open(self.info_dir / ('%s.trashinfo' % name), 'w') as f:
            f.write('[Trash Info]\n'
                    'Path=%s\n'
                    'DeletionDate=2000-01-01T00:00:00\n' % path_line)

    def _restorable(self):
        return [os.path.basename(tf.info_file)
                for tf in self.trashed_files.all_trashed_files(None)]

    def test_a_relative_path_inside_the_volume_is_restorable(self):
        self._add('good', 'docs/report.txt')

        self.assertEqual(['good.trashinfo'], self._restorable())

    def test_an_absolute_path_is_not_restorable(self):
        self._add('evil', '/etc/passwd')

        self.assertEqual([], self._restorable())

    def test_a_path_escaping_the_volume_is_not_restorable(self):
        self._add('evil', '../../../etc/shadow')

        self.assertEqual([], self._restorable())

    def tearDown(self):
        self.volume.clean_up()
