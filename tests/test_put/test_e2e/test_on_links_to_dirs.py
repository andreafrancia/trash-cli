import pytest

from tests.run_command import temp_dir  # noqa
from tests.test_put.test_e2e.run_trash_put.directory_layout import \
    DirectoriesLayout
from trashcli.put.fs.real_fs import RealFs


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
            'file left in current_dir': ['/a-file', '/link-to-dir'],
            'file in trash dir': ['/files',
                                  '/files/link-to-dir',
                                  '/info',
                                  '/info/link-to-dir.trashinfo'],
        }



