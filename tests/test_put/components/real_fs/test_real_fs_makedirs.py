import os
import pytest

from tests.support.format_os_error import format_os_error
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

    def test_makedirs__fail_if_an_intermediate_component_is_a_file(
            self, fs, base_dir):
        fs.touch(base_dir / "foo")

        with pytest.raises(OSError) as e:
            fs.makedirs(base_dir / "foo/bar")

        assert format_os_error(e.value) == {
            'args': "(20, 'Not a directory')\n",
            'errno': '20 ENOTDIR Not a directory\n',
            'filename': base_dir + '/foo/bar\n'}

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

        assert format_os_error(e.value) == {
            'args': "(17, 'File exists')\n",
            'errno': '17 EEXIST File exists\n',
            'filename': base_dir + '/foo\n'}


def _without_exist_ok_kwarg():
    # Simulates os.makedirs on a Python that does not accept the
    # exist_ok keyword argument (available since Python 3.2), so
    # RealFs.makedirs falls back to its manual emulation.
    #
    # Implemented without delegating to the real os.makedirs: its own
    # recursive parent-creation calls back into os.makedirs by name,
    # which would resolve to this very monkeypatched replacement once
    # installed, and fail because it passes exist_ok.
    def makedirs_without_exist_ok(path, mode=0o777):
        parent = os.path.dirname(path)
        if parent and not os.path.isdir(parent):
            makedirs_without_exist_ok(parent, mode)
        os.mkdir(path, mode)

    return makedirs_without_exist_ok
