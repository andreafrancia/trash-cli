import pytest

from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.support.files import     FsFixture
from tests.test_put.cmd.e2e.run_trash_put import run_trash_put
from trashcli.lib.exit_codes import EX_IOERR
from trashcli.fslib.real.real_fs import RealFs

temp_dir = temp_dir_fixture

@pytest.fixture
def fs():
    return FsFixture(RealFs())

@pytest.mark.slow
class TestWhenFedWithDotArguments:

    def test_dot_argument_is_skipped(self, temp_dir):
        result = run_trash_put(temp_dir, ["."])

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be written on stderr
        assert result.combined() == [
            "trash-put: cannot trash directory '.'\n", EX_IOERR]

    def test_dot_dot_argument_is_skipped(self, temp_dir):
        result = run_trash_put(temp_dir, [".."])

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be written on stderr
        assert result.combined() == [
            "trash-put: cannot trash directory '..'\n", EX_IOERR]

    @pytest.mark.parametrize("arg", ["./", ".///", ".//////"])
    def test_dot_with_trailing_slashes_is_skipped(self, temp_dir, fs, arg):
        fs.make_empty_file(temp_dir / 'file')

        result = run_trash_put(temp_dir, [arg])

        assert result.combined() + temp_dir.existence_of(temp_dir / 'file') == [
            "trash-put: cannot trash directory '.'\n", EX_IOERR,
            "/file: exists"]

    @pytest.mark.parametrize("arg", ["../", "..///", "..//////"])
    def test_dot_dot_with_trailing_slashes_is_skipped(self, temp_dir, arg):
        result = run_trash_put(temp_dir, [arg])

        assert result.combined() == [
            "trash-put: cannot trash directory '..'\n", EX_IOERR]

    def test_dot_argument_is_skipped_even_in_subdirs(self, temp_dir, fs):
        sandbox = temp_dir / 'sandbox'
        fs.mkdir_p(sandbox)

        result = run_trash_put(temp_dir, ["%s/." % sandbox])

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be written on stderr
        assert result.combined() + temp_dir.existence_of(sandbox) == [
            "trash-put: cannot trash '.' directory '/sandbox/.'\n",
            EX_IOERR, "/sandbox: exists"]

    def test_dot_dot_argument_is_skipped_even_in_subdirs(self, temp_dir, fs):
        sandbox = temp_dir / 'sandbox'
        fs.mkdir_p(sandbox)

        result = run_trash_put(temp_dir, ["%s/.." % sandbox])

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be written on stderr
        assert result.combined() + temp_dir.existence_of(sandbox) == [
            "trash-put: cannot trash '..' directory '/sandbox/..'\n",
            EX_IOERR, "/sandbox: exists"]
