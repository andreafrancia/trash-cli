import sys

from tests.test_list.cmd.support.trash_list_user import trash_list_user  # noqa

user = trash_list_user


class TestPrintPythonExecutable:
    def test(self, user):
        output = user.run_trash_list('--python')

        assert output.err_and_out() == ('', sys.executable + '\n')
