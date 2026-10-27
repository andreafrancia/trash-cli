import errno
import os

import pytest

from tests.support.dirs.my_path import MyPath
from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.fslib.clean_move import PartlyMoved, clean_move, copy_then_remove
from trashcli.fslib.real.real_fs import RealFs
from trashcli.put.core.either import Left
from trashcli.put.janitor_tools.info_file_persister import TrashedFile
from trashcli.put.janitor_tools.put_trash_dir import PutTrashDir


class FailingFs(FakeFs):
    # a fake fs where chosen renames and copies fail
    def __init__(self):
        super(FailingFs, self).__init__()
        self.failing_sources = []
        self.failing_dests = []
        self.failing_copy = False

    def rename(self, src, dest):
        if src in self.failing_sources or dest in self.failing_dests:
            raise OSError(errno.EIO, "rename failed", src)
        super(FailingFs, self).rename(src, dest)

    def copytree(self, src, dest):
        super(FailingFs, self).copytree(src, dest)
        if self.failing_copy:
            raise OSError(errno.EIO, "copy failed", dest)


class TestCleanMove:
    def setup_method(self):
        self.fs = FailingFs()
        self.fs.add_volume('/other')
        self.fs.makedirs('/other', 0o755)
        self.fs.make_file_and_dirs('/src/dir/a', 'a')
        self.fs.make_file_and_dirs('/src/dir/sub/b', 'b')

    def files(self, path):
        return sorted(p for p in self.fs.find_all() if p.startswith(path))

    def test_a_dir_on_one_volume_is_renamed(self):
        clean_move(self.fs, '/src/dir', '/src/moved')

        assert self.files('/src') == ['/src', '/src/moved', '/src/moved/a',
                                      '/src/moved/sub', '/src/moved/sub/b']

    def test_a_dir_that_cannot_be_renamed_on_one_volume_is_not_copied(self):
        self.fs.chmod('/src', 0o555)

        with pytest.raises(OSError):
            clean_move(self.fs, '/src/dir', '/src/moved')

        assert self.files('/src') == ['/src', '/src/dir', '/src/dir/a',
                                      '/src/dir/sub', '/src/dir/sub/b']

    def test_a_dir_is_copied_to_another_volume_and_removed(self):
        clean_move(self.fs, '/src/dir', '/other/dir')

        assert self.files('/src') + self.files('/other') == [
            '/src', '/other', '/other/dir', '/other/dir/a', '/other/dir/sub',
            '/other/dir/sub/b']

    def test_when_a_removal_step_fails_the_source_is_put_back(self):
        self.fs.failing_sources.append('/src/dir/a')

        with pytest.raises(OSError):
            clean_move(self.fs, '/src/dir', '/other/dir')

        assert self.files('/src') + self.files('/other') == [
            '/src', '/src/dir', '/src/dir/a', '/src/dir/sub', '/src/dir/sub/b',
            '/other']

    def test_when_putting_back_fails_the_copy_is_kept(self):
        self.fs.failing_sources.append('/src/dir/a')
        self.fs.failing_dests.append('/src/dir/sub/b')

        with pytest.raises(PartlyMoved):
            clean_move(self.fs, '/src/dir', '/other/dir')

        assert self.files('/other') == ['/other', '/other/dir', '/other/dir/a',
                                        '/other/dir/sub', '/other/dir/sub/b']
        assert self.fs.read_file('/src/.trash-cli-0/0-b') == 'b'

    def test_when_copying_fails_the_partial_copy_is_removed(self):
        self.fs.failing_copy = True

        with pytest.raises(OSError):
            clean_move(self.fs, '/src/dir', '/other/dir')

        assert self.files('/src') + self.files('/other') == [
            '/src', '/src/dir', '/src/dir/a', '/src/dir/sub', '/src/dir/sub/b',
            '/other']

    def test_trash_put_keeps_the_copy_and_its_trashinfo_when_partly_moved(self):
        self.fs.failing_sources.append('/src/dir/a')
        self.fs.failing_dests.append('/src/dir/sub/b')
        self.fs.make_file_and_dirs('/other/info/dir.trashinfo', 'info')
        self.fs.makedirs('/other/files', 0o755)

        result = PutTrashDir(self.fs).try_trash(
            '/src/dir', TrashedFile('/other/info/dir.trashinfo'))

        assert isinstance(result, Left)
        assert self.files('/other/files') == ['/other/files',
                                              '/other/files/dir',
                                              '/other/files/dir/a',
                                              '/other/files/dir/sub',
                                              '/other/files/dir/sub/b']
        assert self.fs.path_exists('/other/info/dir.trashinfo')


@pytest.mark.skipif(os.geteuid() == 0, reason="root can read any file")
class TestCleanMoveOnRealFs:
    # shutil.copytree() raises shutil.Error, it must be caught by the same except on Python 2 and 3
    def setup_method(self):
        self.tmp_dir = MyPath.make_temp_dir()
        os.makedirs(self.tmp_dir / 'src')
        with open(self.tmp_dir / 'src/unreadable', 'w') as f:
            f.write('x')
        os.chmod(self.tmp_dir / 'src/unreadable', 0)

    def test_a_failed_copy_is_removed_and_the_source_is_kept(self):
        with pytest.raises(EnvironmentError):
            copy_then_remove(RealFs(), self.tmp_dir / 'src', self.tmp_dir / 'dest')

        assert os.path.exists(self.tmp_dir / 'src/unreadable')
        assert not os.path.lexists(self.tmp_dir / 'dest')

    def teardown_method(self):
        os.chmod(self.tmp_dir / 'src/unreadable', 0o600)
        self.tmp_dir.clean_up()
