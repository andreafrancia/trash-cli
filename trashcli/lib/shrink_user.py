import os
import posixpath
import re

from typing import Mapping


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
