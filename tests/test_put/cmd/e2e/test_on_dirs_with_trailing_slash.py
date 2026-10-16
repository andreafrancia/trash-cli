import os

import pytest

from tests.support.dirs.my_path import MyPath
from tests.test_put.cmd.e2e.run_trash_put.directory_layout import \
    DirectoriesLayout
from trashcli.fslib.real.real_fs import RealFs


@pytest.mark.slow
class TestOnDirsWithTrailingSlash:
    def setup_method(self):
        self.fs = RealFs()
        self.temp_dir = MyPath.make_temp_dir()
        self.layout = DirectoriesLayout(self.temp_dir, self.fs)
        self.layout.make_cur_dir()

    def teardown_method(self):
        self.temp_dir.clean_up()

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
