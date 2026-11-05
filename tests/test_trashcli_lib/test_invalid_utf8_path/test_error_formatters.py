from trashcli.compat import TextType
from trashcli.lib.printable import printable
from trashcli.list.list_trash_action import print_non_trashinfo_error
from trashcli.list.list_trash_action import print_parse_path_error


def test_parse_path_error_escapes_raw_bytes():
    message = print_parse_path_error(b'/trash/info/bad\xff.trashinfo')

    assert isinstance(message, TextType)
    assert printable(message) == (
        u'Parse Error: /trash/info/bad\\xff.trashinfo: '
        u'Unable to parse Path.')


def test_non_trashinfo_error_escapes_raw_bytes():
    message = print_non_trashinfo_error(b'/trash/info/bad\xff')

    assert isinstance(message, TextType)
    assert printable(message) == (
        u'Non .trashinfo file in info dir: /trash/info/bad\\xff')


def test_parse_path_error_keeps_a_text_path():
    assert print_parse_path_error(u'/trash/info/caf\xe9.trashinfo') == (
        u'Parse Error: /trash/info/caf\xe9.trashinfo: '
        u'Unable to parse Path.')


def test_non_trashinfo_error_keeps_a_text_path():
    assert print_non_trashinfo_error(u'/trash/info/caf\xe9') == (
        u'Non .trashinfo file in info dir: /trash/info/caf\xe9')
