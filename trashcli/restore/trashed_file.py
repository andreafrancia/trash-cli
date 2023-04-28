import datetime
from logging import Logger
from typing import NamedTuple, Optional

from trashcli.lib.path_of_backup_copy import path_of_backup_copy
from trashcli.parse_trashinfo.parse_original_location import \
    parse_original_location
from trashcli.parse_trashinfo.parse_deletion_date import parse_deletion_date


class TrashedFiles:
    def __init__(self,
                 logger,  # type: Logger
                 trash_directories,
                 trash_directory,
                 contents_of):
        self.logger = logger
        self.trash_directories = trash_directories
        self.trash_directory = trash_directory
        self.contents_of = contents_of

    def all_trashed_files(self, volumes, trash_dir_from_cli):
        for path, volume in self.trash_directories.trash_directories_or_user(
                volumes, trash_dir_from_cli):
            for type, info_file in self.trash_directory.all_info_files(path):
                if type == 'non_trashinfo':
                    self.logger.warning("Non .trashinfo file in info dir")
                elif type == 'trashinfo':
                    try:
                        contents = self.contents_of(info_file)
                        original_location = parse_original_location(contents,
                                                                    volume)
                        deletion_date = parse_deletion_date(contents)
                        backup_file_path = path_of_backup_copy(info_file)
                        trashedfile = TrashedFile(original_location,
                                                  deletion_date,
                                                  info_file,
                                                  backup_file_path)
                        yield trashedfile
                    except ValueError:
                        self.logger.warning("Non parsable trashinfo file: %s" %
                                            info_file)
                    except IOError as e:
                        self.logger.warning(str(e))
                else:
                    self.logger.error("Unexpected file type: %s: %s",
                                      type, info_file)


class TrashedFile(NamedTuple):
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
    original_location: str
    deletion_date: Optional[datetime.datetime]
    info_file: str
    original_file: str
