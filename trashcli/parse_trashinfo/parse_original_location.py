from __future__ import absolute_import

import os

from trashcli.parse_trashinfo.parse_path import parse_path


def parse_original_location(contents, volume_path):
    path = parse_path(contents)
    return os.path.join(volume_path, path)
