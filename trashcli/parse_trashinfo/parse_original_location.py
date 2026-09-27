from __future__ import absolute_import

import os

from trashcli.parse_trashinfo.parse_path import parse_path
from trashcli.parse_trashinfo.parser_error import ParseError


class OriginalLocationParser:
    def __init__(self):
        self.paths = PathOperations()

    def parse_original_location(self, contents, volume_path):
        path = parse_path(contents)
        resolved = self.paths.normpath(self.paths.join(volume_path, path))
        if volume_path != os.path.sep:
            # A volume trash must record a location that is relative to and inside that volume.
            if self.paths.isabs(path):
                raise ParseError("Path= must be relative for volume trashes")
            rel = self.paths.relpath(resolved, self.paths.normpath(volume_path))
            if rel == os.pardir or rel.startswith(os.pardir + os.sep):
                raise ParseError("Path= escapes the volume root")
        return resolved


class PathOperations:
    def normpath(self, path):  # type: (str) -> str
        return os.path.normpath(path)

    def join(self, path, *paths):  # type: (str, *str) -> str
        return os.path.join(path, *paths)

    def isabs(self, path):  # type: (str) -> bool
        return os.path.isabs(path)

    def relpath(self, path, start):  # type: (str, str) -> str
        return os.path.relpath(path, start)
