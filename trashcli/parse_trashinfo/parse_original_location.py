from __future__ import absolute_import

import os

from trashcli.parse_trashinfo.parse_path import parse_path
from trashcli.parse_trashinfo.parser_error import ParseError


def parse_original_location(contents, volume_path):
    path = parse_path(contents)
    if os.path.isabs(path):
        # the home trash legitimately stores absolute paths, on any volume
        return os.path.normpath(path)
    resolved = os.path.normpath(os.path.join(volume_path, path))
    rel = os.path.relpath(resolved, os.path.normpath(volume_path))
    if rel == os.pardir or rel.startswith(os.pardir + os.sep):
        raise ParseError("Path= escapes the volume root")
    return resolved
