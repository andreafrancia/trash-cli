import pytest

from tests.support.temp_dir import temp_dir
from tests.support.files import mkdir_p
from tests.test_put.test_e2e.run_trash_put import run_trash_put
from trashcli.lib.exit_codes import EX_IOERR


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

    def test_dot_argument_is_skipped_even_in_subdirs(self, temp_dir):
        sandbox = temp_dir / 'sandbox'
        mkdir_p(sandbox)

        result = run_trash_put(temp_dir, ["%s/." % sandbox])

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be written on stderr
        assert result.combined() + temp_dir.existence_of(sandbox) == [
            "trash-put: cannot trash '.' directory '/sandbox/.'\n",
            EX_IOERR, "/sandbox: exists"]

    def test_dot_dot_argument_is_skipped_even_in_subdirs(self, temp_dir):
        sandbox = temp_dir / 'sandbox'
        mkdir_p(sandbox)

        result = run_trash_put(temp_dir, ["%s/.." % sandbox])

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be written on stderr
        assert result.combined() + temp_dir.existence_of(sandbox) == [
            "trash-put: cannot trash '..' directory '/sandbox/..'\n",
            EX_IOERR, "/sandbox: exists"]
