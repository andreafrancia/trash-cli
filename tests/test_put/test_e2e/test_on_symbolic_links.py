import os

import pytest

from tests.support.run_command import temp_dir  # noqa
from tests.support.files import make_file
from tests.support.my_path import MyPath
from tests.test_put.test_e2e.run_trash_put import run_trash_put
from trashcli.put.fs.real_fs import RealFs

fs = RealFs()


def _make_connected_link(path):  # type: (MyPath) -> None
    make_file(path.parent / 'link-target')
    os.symlink('link-target', path)


def _make_dangling_link(path):  # type: (MyPath) -> None
    os.symlink('non-existent', path)


@pytest.mark.slow
class TestOnSymbolicLinks:
    def test_trashes_dangling_symlink(self, temp_dir):
        _make_dangling_link(temp_dir / 'link')

        output = run_trash_put(temp_dir, ['link'],
                               env={"TRASH_PUT_DISABLE_SHRINK": "1"})

        assert output.stderr.lines() == [
            "trash-put: 'link' trashed in /trash-dir"]
        assert not os.path.lexists(temp_dir / 'link')
        assert os.path.lexists(temp_dir / 'trash-dir' / 'files' / 'link')

    def test_trashes_connected_symlink(self, temp_dir):
        _make_connected_link(temp_dir / 'link')

        output = run_trash_put(temp_dir, ['link'],
                               env={"TRASH_PUT_DISABLE_SHRINK": "1"})
        assert output.stderr.lines() == ["trash-put: 'link' trashed in /trash-dir"]
        assert not os.path.lexists(temp_dir / 'link')
        assert os.path.lexists(temp_dir / 'trash-dir' / 'files' / 'link')
