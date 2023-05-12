import datetime
import os
from typing import NamedTuple, Optional


class TrashedFile(
    NamedTuple('TrashedFile', [
        ('original_location', str),
        ('deletion_date', Optional[datetime.datetime]),
        ('info_file', str),
        ('original_file', str),
    ])):
    """
    Represent a trashed file.
    Each trashed file is persisted in two files:
     - $trash_dir/info/$id.trashinfo
     - $trash_dir/files/$id

    Properties:
     - path : the original path from where the file has been trashed
     - deletion_date : the time when the file has been trashed (instance of
                       datetime)
     - info_file : the file that contains information (instance of Path)
     - original_file : the path where the trashed file has been placed after the
                       trash operation (instance of Path)
    """

    def original_location_matches_path(self, path):
        if path == os.path.sep:
            return True
        if self.original_location.startswith(path + os.path.sep):
            return True
        return self.original_location == path
