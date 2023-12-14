import os

import pytest

from tests.run_command import run_trash_put_in_tmp_dir
from tests.run_command import temp_dir  # noqa
from tests.support.files import make_file
from tests.support.my_path import MyPath
from trashcli.put.fs.real_fs import RealFs

fs = RealFs()


def _make_connected_link(path):  # type: (MyPath) -> None
    make_file(path.parent / 'link-target')
    os.symlink('link-target', path)


def _make_dangling_link(path):  # type: (MyPath) -> None
    os.symlink('non-existent', path)


@pytest.mark.slow
class TestTrashSymlinks:
    def test_trashes_dangling_symlink(self, temp_dir):
        _make_dangling_link(temp_dir / 'link')

        output = run_trash_put_in_tmp_dir(temp_dir, ['link'],
                                          env={"TRASH_PUT_DISABLE_SHRINK": "1"})

        assert output.stderr.lines() == [
            "trash-put: 'link' trashed in /trash-dir"]
        assert not os.path.lexists(temp_dir / 'link')
        assert os.path.lexists(temp_dir / 'trash-dir' / 'files' / 'link')

    def test_trashes_connected_symlink(self, temp_dir):
        _make_connected_link(temp_dir / 'link')

        output = run_trash_put_in_tmp_dir(temp_dir, ['link'],
                                          env={"TRASH_PUT_DISABLE_SHRINK": "1"})
        assert output.stderr.lines() == ["trash-put: 'link' trashed in /trash-dir"]
        assert not os.path.lexists(temp_dir / 'link')
        assert os.path.lexists(temp_dir / 'trash-dir' / 'files' / 'link')
