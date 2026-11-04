import os
import posixpath
import re

from typing import Mapping

from trashcli.compat import TextType, fsdecode


def _as_text(path):
    if isinstance(path, TextType):
        return path
    return fsdecode(path)


def shrink_user(path,  # type: str
                environ,  # type: Mapping[str, str]
                ):  # type: (...) -> str
    path = os.path.normpath(_as_text(path))
    home_dir = _as_text(environ.get('HOME', ''))
    if home_dir != '':
        home_dir = posixpath.normpath(home_dir)
        path = re.sub('^' + re.escape(home_dir + os.path.sep),
                      '~' + os.path.sep, path)
    return path
