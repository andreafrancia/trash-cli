import pytest

from trashcli.put.fs.parent_realpath import ParentRealpathFs
from tests.support.fs_fixture import real_fs_fixture, fsx_fixture
from tests.support.dirs.temp_dir import temp_dir_fixture

fs = real_fs_fixture
fsx = fsx_fixture
temp_dir = temp_dir_fixture


@pytest.mark.slow
class TestParentPath:
    @pytest.fixture(autouse=True)
    def setup_fs(self, fsx):
        self.fsx = fsx

    @pytest.fixture(autouse=True)
    def setup_sut(self, fs):
        self.parent_realpath = ParentRealpathFs(fs).parent_realpath

    def test(self, fs, temp_dir, fsx):
        self.fsx.require_empty_dir(temp_dir / 'other_dir/dir')
        fs.symlink(temp_dir / 'other_dir/dir', temp_dir / 'dir')
        self.fsx.make_empty_file(temp_dir / 'dir/foo')

        result = self.parent_realpath(temp_dir / 'dir/foo')

        assert result == temp_dir / 'other_dir/dir'

    def test2(self, fs, temp_dir, fsx):
        self.fsx.require_empty_dir(temp_dir / 'test-disk/dir')
        fs.symlink(temp_dir / 'test-disk/non-existent',
                   temp_dir / 'link-to-non-existent')

        result = self.parent_realpath(temp_dir / 'link-to-non-existent')

        assert result == temp_dir

    def test3(self, fs, temp_dir, fsx):
        self.fsx.require_empty_dir(temp_dir / 'foo')
        self.fsx.require_empty_dir(temp_dir / 'bar')
        fs.symlink('../bar/zap', temp_dir / 'foo/zap')

        result = self.parent_realpath(temp_dir / 'foo/zap')

        assert result == temp_dir / 'foo'

    def test4(self, fs, temp_dir, fsx):
        self.fsx.require_empty_dir(temp_dir / 'foo')
        self.fsx.require_empty_dir(temp_dir / 'bar')
        fs.symlink('../bar/zap', temp_dir / 'foo/zap')
        self.fsx.make_empty_file(temp_dir / 'bar/zap')

        result = self.parent_realpath(temp_dir / 'foo/zap')

        assert result == temp_dir / 'foo'
