import os
import unittest

from tests.support.dirs.my_path import MyPath
from trashcli.empty.top_trash_dir_rules_file_system_reader import \
    RealTopTrashDirRulesReader
from trashcli.fstab.volumes import FakeVolumes2
from trashcli.restore.trash_directories import TrashDirectories1
from trashcli.trash_dirs_scanner import TopTrashDirRules


class RecordingLogger:
    def __init__(self):
        self.warnings = []

    def warning(self, message):
        self.warnings.append(message)


class TestRestoreDistrustsUnsafeTrashDirs(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.environ = {'HOME': self.tmp_dir}
        self.volumes = FakeVolumes2("volume_of(%s)", [])
        self.rules = TopTrashDirRules(RealTopTrashDirRulesReader())
        self.home_trash = self.tmp_dir / '.local' / 'share' / 'Trash'
        self.logger = RecordingLogger()

    def _dirs(self):
        td = TrashDirectories1(self.volumes, 123, self.environ, self.rules,
                               self.logger)
        return [p for p, v in td.all_trash_directories()]

    def test_a_normal_home_trash_is_kept(self):
        os.makedirs(self.home_trash / 'info')

        assert str(self.home_trash) in self._dirs()

    def test_a_symlinked_info_dir_is_skipped(self):
        os.makedirs(self.home_trash)
        os.symlink('/tmp', self.home_trash / 'info')

        assert self._dirs() == []

    def test_a_world_writable_info_dir_is_skipped(self):
        os.makedirs(self.home_trash / 'info')
        os.chmod(self.home_trash / 'info', 0o0777)

        assert self._dirs() == []

    def test_a_world_writable_files_dir_is_skipped(self):
        os.makedirs(self.home_trash / 'info')
        os.makedirs(self.home_trash / 'files')
        os.chmod(self.home_trash / 'files', 0o0777)

        assert self._dirs() == []

    def test_a_skipped_dir_is_reported(self):
        os.makedirs(self.home_trash / 'info')
        os.chmod(self.home_trash / 'info', 0o0777)

        self._dirs()

        assert self.logger.warnings == [
            "TrashDir skipped because it is not secure: %s" % self.home_trash]

    def tearDown(self):
        self.tmp_dir.clean_up()
