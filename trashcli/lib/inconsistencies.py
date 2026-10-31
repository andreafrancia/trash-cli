from typing import Mapping

from trashcli.lib.shrink_user import shrink_user


def inconsistencies_found(trash_dir,  # type: str
                          environ,  # type: Mapping[str, str]
                          ):  # type: (...) -> str
    return ("Found inconsistencies in %s check them running "
            "`trash-list --doctor`" % shrink_user(trash_dir, environ))
