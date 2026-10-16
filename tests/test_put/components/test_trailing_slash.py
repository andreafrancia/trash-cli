import pytest

from trashcli.put.context import without_trailing_slashes


@pytest.mark.parametrize("path, expected", [
    ("dir", "dir"),
    ("dir/", "dir"),
    ("dir//", "dir"),
    ("dir//////", "dir"),
    ("a/../b/", "a/../b"),
    ("/", "/"),
])
def test_without_trailing_slashes(path, expected):
    assert without_trailing_slashes(path) == expected
