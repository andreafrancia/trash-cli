from trashcli.lib.inconsistencies import inconsistencies_check_hint
from trashcli.lib.inconsistencies import inconsistencies_found
from trashcli.lib.printable import printable


def test_summary_returns_text_for_a_byte_path():
    summary = inconsistencies_found(
        b'/home/user/.local/share/Trash/caf\xc3\xa9',
        {'HOME': b'/home/user'})

    expected = u'Found inconsistencies in ~/.local/share/Trash/caf\xe9'
    assert summary == expected
    assert printable(summary) == expected


def test_hint_keeps_selected_trash_dirs():
    assert inconsistencies_check_hint(['/custom']) == (
        "To check all inconsistencies run: `trash-list --doctor "
        "--trash-dir /custom`")
