import pytest

from tests.support.dirs.my_path import MyPath
from tests.support.dirs.support_fs import SupportFs
from tests.support.dirs.temp_dir import temp_dir_fixture_fs
from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.fslib.protocols.fs import Fs
from trashcli.put.janitor_tools.put_trash_dir import move_file

temp_dir = temp_dir_fixture_fs

class TestMoveFile:
    @pytest.fixture
    def fs(self):
        return FakeFs()

    @pytest.fixture
    def support_fs(self, fs, temp_dir):
        return SupportFs(fs, temp_dir)

    @pytest.mark.slow
    def test_delete_when_trailing_slash(self,
                                       fs,  # type: Fs
                                       support_fs,  # type: SupportFs
                                       temp_dir,  # type: MyPath
                                       ):
        support_fs.mkdir_rel("dir")
        support_fs.symlink_rel("dir", "link-to-dir")

        move_file(fs, temp_dir / "link-to-dir/", temp_dir / "trash-location")

        assert support_fs.list_all_files_sorted() == ['/dir', '/trash-location']
