from __future__ import absolute_import

import os

from trashcli.parse_trashinfo.parse_path import parse_path
from trashcli.parse_trashinfo.parser_error import ParseError


def parse_original_location(contents, volume_path):
    # Per spec: Path= is absolute only for the home trash (volume=='/');
    # for volume trashes it must resolve under volume_path.
    path = parse_path(contents)
    resolved = os.path.normpath(os.path.join(volume_path, path))
    if volume_path != os.path.sep:
        if os.path.isabs(path):
            raise ParseError("Path= must be relative for volume trashes")
        rel = os.path.relpath(resolved, os.path.normpath(volume_path))
        if rel == '..' or rel.startswith('..' + os.sep):
            raise ParseError("Path= escapes the volume root")
    return resolved
