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

    def test_makedirs__use_the_given_mode(self, fs, base_dir, process_umask):
        fs.makedirs(base_dir / "foo", mode=0o700)

        expected_mode = 0o700 & ~process_umask
        assert fs.get_mod(base_dir / "foo") == expected_mode

    def test_makedirs__fail_if_an_intermediate_component_is_a_file(
            self, fs, base_dir):
        fs.touch(base_dir / "foo")

        with pytest.raises(OSError) as e:
            fs.makedirs(base_dir / "foo/bar")

        assert _describe_os_error(e.value) == {
            'args': "(20, 'Not a directory')\n",
            'errno': '20 ENOTDIR Not a directory\n',
            'filename': base_dir + '/foo/bar\n'}

    def test_makedirs__with_exist_ok__still_fail_if_path_is_a_file(
            self, fs, base_dir):
        fs.touch(base_dir / "foo")

        with pytest.raises(OSError) as e:
            fs.makedirs(base_dir / "foo", exist_ok=True)

        assert _describe_os_error(e.value) == {
            'args': "(17, 'File exists')\n",
            'errno': '17 EEXIST File exists\n',
            'filename': base_dir + '/foo\n'}

    def test_makedirs__legacy_fallback__creates_dir(
            self, fs, base_dir, monkeypatch):
        monkeypatch.setattr(os, 'makedirs', _without_exist_ok_kwarg())

        fs.makedirs(base_dir / "foo/bar")

        assert fs.path_isdir(base_dir / "foo/bar") == True

    def test_makedirs__legacy_fallback__exist_ok_suppresses_existing_dir_error(
            self, fs, base_dir, monkeypatch):
        fs.mkdir(base_dir / "foo")
        monkeypatch.setattr(os, 'makedirs', _without_exist_ok_kwarg())

        fs.makedirs(base_dir / "foo", exist_ok=True)

        assert fs.path_isdir(base_dir / "foo") == True

    def test_makedirs__legacy_fallback__without_exist_ok_still_fails_if_dir_exists(
            self, fs, base_dir, monkeypatch):
        fs.mkdir(base_dir / "foo")
        monkeypatch.setattr(os, 'makedirs', _without_exist_ok_kwarg())

        with pytest.raises(OSError) as e:
            fs.makedirs(base_dir / "foo")

        assert _describe_os_error(e.value) == {
            'args': "(17, 'File exists')\n",
            'errno': '17 EEXIST File exists\n',
            'filename': base_dir + '/foo\n'}


def _describe_os_error(e):
    return {
        "errno": str(e.errno) + " " +
                 errno.errorcode[e.errno] + " " +
                 os.strerror(e.errno) + "\n",
        "filename": e.filename + "\n",
        "args": str(e.args) + "\n",
    }

def _without_exist_ok_kwarg():
    # Simulates os.makedirs on a Python that does not accept the
    # exist_ok keyword argument (available since Python 3.2), so
    # RealFs.makedirs falls back to its manual emulation.
    real_makedirs = os.makedirs

    def makedirs_without_exist_ok(path, mode=0o777):
        return real_makedirs(path, mode)

    return makedirs_without_exist_ok
