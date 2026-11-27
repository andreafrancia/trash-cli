import pytest

from tests.support.dirs.my_path import MyPath
from tests.support.dirs.support_fs import SupportFs
from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.support.fs_fixture import real_fs_fixture
from tests.support.fs_fixture import fsx_fixture
from tests.support.fs_fixture import FsFixture
from tests.support.fs_fixture import support_fs_fixture
from tests.test_put.cmd.e2e.run_trash_put import run_trash_put
from trashcli.lib.exit_codes import EX_IOERR

fs = real_fs_fixture
temp_dir = temp_dir_fixture
fsx = fsx_fixture
support_fs = support_fs_fixture


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
    def test_dot_with_trailing_slashes_is_skipped(
            self,
            temp_dir,  # type: MyPath
            fsx,  # type: FsFixture
            support_fs,  # type: SupportFs
            arg,
    ):
        fsx.make_empty_file(temp_dir / 'file')

        result = run_trash_put(temp_dir, [arg])

        assert result.combined() + support_fs.existence_of(
            temp_dir / 'file') == [
                   "trash-put: cannot trash directory '.'\n", EX_IOERR,
                   "/file: exists"]

    @pytest.mark.parametrize("arg", ["../", "..///", "..//////"])
    def test_dot_dot_with_trailing_slashes_is_skipped(
            self,
            temp_dir,  # type: MyPath
            arg,  # type: str
    ):
        result = run_trash_put(temp_dir, [arg])

        assert result.combined() == [
            "trash-put: cannot trash directory '..'\n", EX_IOERR]

    def test_dot_argument_is_skipped_even_in_subdirs(
            self,
            temp_dir,  # type: MyPath
            fsx,  # type: FsFixture
            support_fs,  # type: SupportFs
    ):
        sandbox = temp_dir / 'sandbox'
        fsx.mkdir_p(sandbox)

        result = run_trash_put(temp_dir, ["%s/." % sandbox])

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be written on stderr
        assert result.combined() + support_fs.existence_of(sandbox) == [
            "trash-put: cannot trash '.' directory '/sandbox/.'\n",
            EX_IOERR, "/sandbox: exists"]

    def test_dot_dot_argument_is_skipped_even_in_subdirs(
            self,
            temp_dir,  # type: MyPath
            fsx,  # type: FsFixture
            support_fs,  # type: SupportFs
    ):
        sandbox = temp_dir / 'sandbox'
        fsx.mkdir_p(sandbox)

        result = run_trash_put(temp_dir, ["%s/.." % sandbox])

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be written on stderr
        assert result.combined() + support_fs.existence_of(sandbox) == [
            "trash-put: cannot trash '..' directory '/sandbox/..'\n",
            EX_IOERR, "/sandbox: exists"]
