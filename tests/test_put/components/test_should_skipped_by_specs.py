import os

import pytest

from trashcli.put.core.trashee import should_skipped_by_specs


@pytest.mark.parametrize("path, expected", [
    (".", True),
    ("..", True),
    ("dir/.", True),
    ("dir/..", True),
    ("dir", False),
    ("dir/sub", False),
])
def test_should_skipped_by_specs(path, expected):
    assert should_skipped_by_specs(path) == expected


# plain basename and normalized basename differ, strip the slash first
@pytest.mark.parametrize("path, plain, normalized", [
    ("./", "", "."),
    ("a/b/..", "..", "a"),
])
def test_plain_basename_differs_from_normalized_basename(path, plain,
                                                         normalized):
    assert os.path.basename(path) == plain
    assert os.path.basename(os.path.normpath(path)) == normalized
