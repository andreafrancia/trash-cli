import os

import pytest

from tests.test_put.cmd.e2e.run_trash_put.directory_layout import \
    DirectoriesLayout

from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.support.fs_fixture import real_fs_fixture

fs = real_fs_fixture
temp_dir = temp_dir_fixture

@pytest.mark.slow
class TestOnDirsWithTrailingSlash:
    @pytest.fixture(autouse=True)
    def setup_fs(self, fs, temp_dir):
        self.fs = fs
        self.temp_dir = temp_dir
        self.layout = DirectoriesLayout(self.temp_dir, self.fs)
        self.layout.make_cur_dir()

    @pytest.mark.skipif(os.geteuid() == 0, reason="root can delete anyway")
    def test_dir_in_a_read_only_parent_is_refused(self):
        self.fs.makedirs(self.layout.cur_dir / 'parent/dir', 0o755)
        self.fs.touch(self.layout.cur_dir / 'parent/dir/file')
        self.fs.chmod(self.layout.cur_dir / 'parent', 0o555)

        result = self.layout.run_trash_put(['parent/dir/'])
        self.fs.chmod(self.layout.cur_dir / 'parent', 0o755)

        assert result.status() == {
            'command output': "trash-put: cannot trash directory "
                              "'parent/dir' because deleting it is not "
                              "allowed",
            'file left in current_dir': ['/parent',
                                         '/parent/dir',
                                         '/parent/dir/file'],
            'file in trash dir': [],
        }

    def test_read_only_dir_is_trashed(self):
        self.fs.makedirs(self.layout.cur_dir / 'dir', 0o555)

        result = self.layout.run_trash_put(['dir/'])

        assert result.status() == {
            'command output': "trash-put: 'dir' trashed in /trash-dir",
            'file left in current_dir': [],
            'file in trash dir': ['/files',
                                  '/files/dir',
                                  '/info',
                                  '/info/dir.trashinfo'],
        }
