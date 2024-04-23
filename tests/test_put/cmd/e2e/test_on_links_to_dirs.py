import pytest

from tests.support.dirs.temp_dir import temp_dir
from tests.test_put.cmd.e2e.run_trash_put.directory_layout import \
    DirectoriesLayout
from trashcli.put.fs.real_fs import RealFs

temp_dir = temp_dir


@pytest.mark.slow
class TestOnLinksToDirs:
    def test_link_to_dir_without_slashes(self, temp_dir):
        layout = DirectoriesLayout(temp_dir, RealFs())
        layout.make_cur_dir()
        layout.mkdir_in_cur_dir('a-dir')
        layout.touch_in_cur_dir('a-file')
        layout.symlink_in_cur_dir('a-dir', 'link-to-dir')

        result = layout.run_trash_put(['link-to-dir'])

        assert result.status() == {
            'command output': "trash-put: 'link-to-dir' trashed in /trash-dir",
            'file left in current_dir': ['/a-dir', '/a-file'],
            'file in trash dir': ['/files',
                                  '/files/link-to-dir',
                                  '/info',
                                  '/info/link-to-dir.trashinfo'],
        }

    def test_link_to_dir_with_slashes(self, temp_dir):
        layout = DirectoriesLayout(temp_dir, RealFs())
        layout.make_cur_dir()
        layout.mkdir_in_cur_dir("a-dir")
        layout.touch_in_cur_dir("a-file")
        layout.symlink_in_cur_dir('a-dir', 'link-to-dir')

        result = layout.run_trash_put(['link-to-dir/'])

        assert result.status() == {
            'command output': "trash-put: 'link-to-dir/' trashed in /trash-dir",
            'file left in current_dir': ['/a-dir', '/a-file'],
            'file in trash dir': ['/files',
                                  '/files/link-to-dir',
                                  '/info',
                                  '/info/link-to-dir.trashinfo'],
        }
