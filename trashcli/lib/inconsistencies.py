"""
Helpers for formatting the user-facing messages about inconsistencies found
in trash directories. This module only formats text; it does not scan or
decide anything.
"""
from typing import Mapping

from trashcli.lib.shrink_user import shrink_user


def inconsistencies_found(trash_dir,  # type: str
                          environ,  # type: Mapping[str, str]
                          ):  # type: (...) -> str
    return "Found inconsistencies in %s" % shrink_user(trash_dir, environ)


def inconsistencies_check_hint():  # type: () -> str
    return "To check all inconsistencies run: `trash-list --doctor`"
