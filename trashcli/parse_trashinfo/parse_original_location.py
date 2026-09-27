from __future__ import absolute_import

import os

from trashcli.parse_trashinfo.parse_path import parse_path
from trashcli.parse_trashinfo.parser_error import ParseError
from trashcli.put.fs.real_volume_path_fs import RealVolumePathFs
from trashcli.put.fs.volume_path_fs import VolumePathFs


class OriginalLocationParser:
    def __init__(self):
        self.volume_paths = RealVolumePathFs()  # type: VolumePathFs

    def parse_original_location(self, contents, volume_path):
        path = parse_path(contents)
        resolved = os.path.normpath(os.path.join(volume_path, path))
        if not self.volume_paths.is_root_volume(volume_path):
            # A volume trash must record a location that is relative to and inside that volume.
            if os.path.isabs(path):
                raise ParseError("Path= must be relative for volume trashes")
            if self.volume_paths.is_outside_of(resolved, volume_path):
                raise ParseError("Path= escapes the volume root")
        return resolved
