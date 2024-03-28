import os.path

import pytest

from tests.run_command import temp_dir  # noqa
from tests.support.my_path import MyPath
from trashcli.put.fs.real_fs import RealFs
from trashcli.put.janitor_tools.put_trash_dir import move_file


class TestMoveFile:
    @pytest.mark.slow
    def test_delete_when_traling_slash(self,
                                       temp_dir):  # type: (MyPath) -> None
        fs = RealFs()
        temp_dir.mkdir_rel("dir")
        temp_dir.symlink_rel("dir", "link-to-dir")

        move_file(fs, temp_dir / "link-to-dir/", temp_dir / "trash-location")

        assert fs.listdir(temp_dir) == ['trash-location', 'dir']
