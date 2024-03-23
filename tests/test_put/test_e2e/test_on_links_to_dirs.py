import os

import pytest

from tests.run_command import temp_dir  # noqa
from tests.test_put.test_e2e.run_trash_put import run_trash_put
from trashcli.put.fs.real_fs import RealFs

fs = RealFs()


@pytest.mark.slow
class TestOnLinksToDirs:
    def test_link_to_dir_without_slashes(self, temp_dir):
        fs.mkdir(temp_dir / 'a-dir')
        fs.touch(temp_dir / "a-file")

        fs.symlink(temp_dir / 'a-dir', temp_dir / 'link-to-dir')

        output = run_trash_put(temp_dir, ['link-to-dir'])

        assert output.stderr.lines() == [
            "trash-put: 'link-to-dir' trashed in /trash-dir"
        ]
        assert fs.list_sorted(temp_dir) == ['a-dir', 'a-file', 'trash-dir']

    def test_link_to_dir_with_slashes(self, temp_dir):
        fs.mkdir(temp_dir / 'a-dir')
        fs.touch(temp_dir / "a-file")

        fs.symlink(temp_dir / 'a-dir', temp_dir / 'link-to-dir')

        output = run_trash_put(temp_dir, ['link-to-dir/'])

        assert temp_dir.list_all_files_sorted() == [
            '/a-file',
            '/link-to-dir',
            '/trash-dir',
            '/trash-dir/files',
            '/trash-dir/files/link-to-dir',
            '/trash-dir/info',
            '/trash-dir/info/link-to-dir.trashinfo']
        assert output.stderr.lines() == [
            "trash-put: 'link-to-dir/' trashed in /trash-dir"]
        assert fs.list_sorted(temp_dir) == ['a-file',
                                            'link-to-dir',
                                            'trash-dir']
