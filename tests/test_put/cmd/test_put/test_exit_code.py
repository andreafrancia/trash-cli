from tests.test_put.cmd.test_put.put_fixture import PutFixture
from trashcli.lib.exit_codes import EX_IOERR
from trashcli.lib.exit_codes import EX_OK


class TestPut(PutFixture):

    def test_exit_code_will_be_0_when_trash_succeeds(self, user, fs):
        fs.touch("pippo")

        result = user.run_cmd(['trash-put', 'pippo'])

        assert result.exit_code == EX_OK

    def test_exit_code_will_be_non_0_when_trash_fails(self, user, fs):
        fs.assert_does_not_exist("a")

        result = user.run_cmd(['trash-put', 'a'])

        assert result.exit_code == EX_IOERR

    def test_exit_code_will_be_non_0_when_just_one_trash_fails(self, user, fs):
        fs.touch("a")
        fs.assert_does_not_exist("b")
        fs.touch("c")

        result = user.run_cmd(['trash-put', 'a', 'b', 'c'])

        assert result.exit_code == EX_IOERR

