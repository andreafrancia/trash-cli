"""
Helpers for formatting the user-facing messages about inconsistencies found
in trash directories. This module only formats text; it does not scan or
decide anything.
"""
from typing import List, Mapping, Optional

from trashcli.compat import fsdecode_text
from trashcli.lib.sanitize import shell_escape
from trashcli.lib.shrink_user import shrink_user


def inconsistencies_found(trash_dir,  # type: str
                          environ,  # type: Mapping[str, str]
                          ):  # type: (...) -> str
    return "Found inconsistencies in %s" % shrink_user(trash_dir, environ)


def inconsistencies_check_hint(
        trash_dirs=None,  # type: Optional[List[str]]
        all_users=False,  # type: bool
        ):  # type: (...) -> str
    command = "trash-list --doctor"
    if all_users:
        command += " --all-users"
    elif trash_dirs:
        for trash_dir in trash_dirs:
            command += " --trash-dir %s" % shell_escape(
                fsdecode_text(trash_dir))
    return "To check all inconsistencies run: `%s`" % command
