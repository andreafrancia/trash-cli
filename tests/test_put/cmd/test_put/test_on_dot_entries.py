from tests.test_put.cmd.test_put.put_fixture import PutFixture
from trashcli.lib.exit_codes import EX_IOERR


class TestPut(PutFixture):


    def test_should_not_trash_dot_entry(self, user, fs):
        result = user.run_cmd(['trash-put', '.'])

        assert result.exit_code_and_stderr() == [
            EX_IOERR,
            ["trash-put: cannot trash directory '.'"]]

    def test_should_not_trash_dot_dot_entry(self, user):
        result = user.run_cmd(['trash-put', '..'])

        assert result.exit_code_and_stderr() == [
            EX_IOERR,
            ["trash-put: cannot trash directory '..'"]]
