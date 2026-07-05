from six import StringIO

from tests.test_list.cmd.support.trash_list_user import trash_list_user


class Tty(StringIO):
    def isatty(self):
        return True


class Pipe(StringIO):
    def isatty(self):
        return False


def test_on_a_terminal_the_name_is_shell_escaped(trash_list_user):
    trash_list_user.home_trash_dir().add_trashinfo4('/tmp/weird\rname',
                                                    "2001-01-01 00:00:00")
    out = Tty()
    trash_list_user.stdout = out

    trash_list_user.run_trash_list()

    output = out.getvalue()
    assert "'/tmp/weird'$'\\r''name'" in output
    assert '\r' not in output


def test_when_piped_the_name_is_printed_raw(trash_list_user):
    trash_list_user.home_trash_dir().add_trashinfo4('/tmp/weird\rname',
                                                    "2001-01-01 00:00:00")
    out = Pipe()
    trash_list_user.stdout = out

    trash_list_user.run_trash_list()

    assert '/tmp/weird\rname' in out.getvalue()
