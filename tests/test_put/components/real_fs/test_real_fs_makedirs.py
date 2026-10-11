import pytest

from tests.support.dirs.temp_dir import temp_dir_fixture
from trashcli.fslib.real.real_fs import RealFs

@pytest.mark.slow
class TestRealFsMakedirs:
    @pytest.fixture
    def fs(self):
        return RealFs()
    @pytest.fixture
    def base_dir(self, temp_dir_fixture):
        return temp_dir_fixture

    def test_makedirs__use_0o777__when_mode_is_not_specified(
            self, fs, base_dir, process_umask):
        fs.makedirs(base_dir / "foo/bar/baz")

        expected_mode = 0o777 & ~process_umask

        assert [
                   fs.path_isdir(base_dir / "foo/bar/baz"),
                   fs.get_mod(base_dir / "foo/bar/baz"),
               ] == [True, expected_mode]

    def test_makedirs__fail_if_dir_exists(self, fs, base_dir):
        fs.mkdir(base_dir / "foo")

        with pytest.raises(OSError) as e:
            fs.makedirs(base_dir / "foo")

        import errno
        import os
        assert isinstance(e.value, OSError)
        assert str(e.value) == "[Errno 17] File exists: '" + base_dir / "foo'"
        assert e.value.errno == errno.EEXIST
        assert e.value.args == (errno.EEXIST, os.strerror(errno.EEXIST))
        assert 'File exists' == os.strerror(errno.EEXIST)

    def test_makedirs__with_exists_ok__wont_file_if_dir_exists(
            self,
            fs,
            base_dir,
    ):
        fs.mkdir(base_dir / "foo")
        assert fs.path_isdir(base_dir / "foo") == True

        fs.makedirs(base_dir / "foo", exist_ok=True)

        assert fs.path_isdir(base_dir / "foo") == True
