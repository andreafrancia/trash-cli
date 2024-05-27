from tests.test_put.cmd.test_put.put_fixture import PutFixture
from trashcli.lib.exit_codes import EX_OK


class TestInteractive(PutFixture):
    def test_user_reply_no(self, user, fs):
        fs.touch("foo")
        user.set_user_reply('n')

        result = user.run_cmd(['trash-put', '-i', 'foo'])

        assert result.exit_code_and_stderr() + [user.last_user_prompt(),
                                                fs.ls_existing(
                                                    ["foo"])] == [
                   EX_OK, [], "trash-put: trash regular empty file 'foo'? ",
                   ['foo'],
               ]

    def test_user_reply_yes(self, user, fs):
        fs.touch("foo")
        user.set_user_reply('y')

        result = user.run_cmd(['trash-put', '-i', 'foo'])

        assert result.exit_code_and_stderr() + [user.last_user_prompt(),
                                                fs.ls_existing(
                                                    ["foo"])] == [
                   EX_OK, [], "trash-put: trash regular empty file 'foo'? ",
                   []
               ]
