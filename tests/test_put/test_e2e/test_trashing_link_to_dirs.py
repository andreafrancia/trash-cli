import os

import pytest

from tests.run_command import run_trash_put_in_tmp_dir
from tests.run_command import temp_dir
from trashcli.put.fs.real_fs import RealFs

fs = RealFs()

temp_dir = temp_dir


@pytest.mark.slow
class TestTrashingLinkToDirs:
    def test_link_to_dir_without_slashes(self, temp_dir):
        fs.mkdir(temp_dir / 'a-dir')
        fs.touch(temp_dir / "a-file")

        fs.symlink(temp_dir / 'a-dir', temp_dir / 'link-to-dir')

        stderr = run_trash_put_in_tmp_dir(temp_dir, ['link-to-dir'])

        assert stderr == [
            "trash-put: 'link-to-dir' trashed in /trash-dir"
        ]
        assert os.listdir(temp_dir) == ['a-file', 'a-dir', 'trash-dir']

    def test_link_to_dir_with_slashes(self, temp_dir):
        fs.mkdir(temp_dir / 'a-dir')
        fs.touch(temp_dir / "a-file")

        fs.symlink(temp_dir / 'a-dir', temp_dir / 'link-to-dir')

        stderr = run_trash_put_in_tmp_dir(temp_dir, ['link-to-dir/'])

        assert stderr == ["trash-put: 'link-to-dir/' trashed in /trash-dir"]
        assert os.listdir(temp_dir) == ['link-to-dir',
                                        'a-file',
                                        'trash-dir']
