from __future__ import absolute_import

import os

from trashcli.lib.trash_dirs import is_volume_trash_dir
from trashcli.parse_trashinfo.parse_path import parse_path
from trashcli.parse_trashinfo.parser_error import ParseError
from trashcli.put.fs.volume_path_fs import VolumePathFs


class OriginalLocationParser:

    def parse_original_location(self, contents, volume_path, trash_dir):
        path = parse_path(contents)
        resolved = os.path.normpath(os.path.join(volume_path, path))
        # the home trash (or any other trash dir) may live on a mount point other than / and still record absolute paths
        if (is_volume_trash_dir(trash_dir, volume_path) and
                not VolumePathFs().is_root_volume(volume_path)):
            # A volume trash must record a location that is relative to and inside that volume.
            if os.path.isabs(path):
                raise ParseError("Path= must be relative for volume trashes")
            if VolumePathFs().is_outside_of(resolved, volume_path):
                raise ParseError("Path= escapes the volume root")
        return resolved
