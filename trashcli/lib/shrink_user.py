import os
import posixpath
import re

from typing import Mapping

from trashcli.compat import fsdecode_text


def shrink_user(path,  # type: str
                environ,  # type: Mapping[str, str]
                ):  # type: (...) -> str
    path = os.path.normpath(fsdecode_text(path))
    home_dir = fsdecode_text(environ.get('HOME', ''))
    if home_dir != '':
        home_dir = posixpath.normpath(home_dir)
        path = re.sub('^' + re.escape(home_dir + os.path.sep),
                      '~' + os.path.sep, path)
    return path
