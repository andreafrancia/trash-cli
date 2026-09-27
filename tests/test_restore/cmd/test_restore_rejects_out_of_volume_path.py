import collections
import os

from tests.support.dirs.my_path import MyPath
from trashcli.put.fs.real_volume_path_fs import RealVolumePathFs
from trashcli.restore.restore_fs import FileReaderFs
from trashcli.restore.trashed_files import TrashedFiles


InfoFile = collections.namedtuple('InfoFile', 'path type volume')


class FakeReaderFs(FileReaderFs):
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


# Security tests of TrashedFiles (see commit 6cd261cd "Prevent restore from
# escaping the trash volume"). The trash dir is a volume trash
# (<volume>/.Trash-1000) on a volume that is not '/', so by the freedesktop
# trash spec its Path= entries must be relative to the volume. A .trashinfo
# that would restore a file outside of the volume must not be offered for
# restore, otherwise anybody able to write in a trash dir on a removable or
# shared volume could make the user overwrite arbitrary files.
class TestRestoreRejectsOutOfVolumePath:
    def setup_method(self):
        self.volume = MyPath.make_temp_dir()
        self.info_dir = self.volume / '.Trash-1000' / 'info'
        os.makedirs(self.info_dir)
        self.logger = MemoLogger()
        self.trashed_files = TrashedFiles(self.logger, FakeReaderFs(),
                                          FakeSearcher(self.info_dir,
                                                       self.volume),
                                          RealVolumePathFs())

    def _add(self, name, path_line):
        with open(self.info_dir / ('%s.trashinfo' % name), 'w') as f:
            f.write('[Trash Info]\n'
                    'Path=%s\n'
                    'DeletionDate=2000-01-01T00:00:00\n' % path_line)

    def _restorable(self):
        return [os.path.basename(tf.info_file)
                for tf in self.trashed_files.all_trashed_files(None)]

    # Purpose: the legitimate case still works: a relative Path= inside the
    # volume is listed as restorable.
    def test_a_relative_path_inside_the_volume_is_restorable(self):
        self._add('good', 'docs/report.txt')

        assert ['good.trashinfo'] == self._restorable()

    # Purpose: an absolute Path= in a volume trash is refused (it could point
    # anywhere, e.g. /etc/passwd).
    def test_an_absolute_path_is_not_restorable(self):
        self._add('evil', '/etc/passwd')

        assert [] == self._restorable()

    # Purpose: a relative Path= that climbs out of the volume with '..' is
    # refused as well.
    def test_a_path_escaping_the_volume_is_not_restorable(self):
        self._add('evil', '../../../etc/shadow')

        assert [] == self._restorable()

    def teardown_method(self):
        self.volume.clean_up()
