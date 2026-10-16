import os
import posixpath
import re

from typing import Mapping


def inconsistencies_found(trash_dir,  # type: str
                          environ,  # type: Mapping[str, str]
                          ):  # type: (...) -> str
    return ("Found inconsistencies in %s check them running "
            "`trash-list --doctor`" % shrink_user(trash_dir, environ))


def shrink_user(path,  # type: str
                environ,  # type: Mapping[str, str]
                ):  # type: (...) -> str
    path = os.path.normpath(path)
    home_dir = environ.get('HOME', '')
    if home_dir != '':
        home_dir = posixpath.normpath(home_dir)
        path = re.sub('^' + re.escape(home_dir + os.path.sep),
                      '~' + os.path.sep, path)
    return path
