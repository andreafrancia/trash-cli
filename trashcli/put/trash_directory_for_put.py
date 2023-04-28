import os

from trashcli.put.candidate import Candidate
from trashcli.put.clock import PutClock
from trashcli.put.format_trash_info import format_trashinfo
from trashcli.put.fs.fs import Fs
from trashcli.put.info_dir import InfoDir
from trashcli.put.my_logger import LogData
from trashcli.put.original_location import OriginalLocation
from trashcli.lib.path_of_backup_copy import path_of_backup_copy


class TrashDirectoryForPut:
    def __init__(self,
                 fs,  # type: Fs
                 info_dir,  # type: InfoDir
                 original_location,  # type: OriginalLocation
                 clock,  # type: PutClock
                 ):
        self.fs = fs
        self.info_dir = info_dir
        self.original_location = original_location
        self.clock = clock

    def trash2(self,
               path,
               candidate,  # type: Candidate
               log_data,  # type: LogData
               ):
        original_location = self.original_location.for_file(
            path, candidate.path_maker_type, candidate.volume)
        basename = os.path.basename(original_location)
        content = format_trashinfo(original_location, self.clock.now())
        trash_info_file = self.info_dir.persist_trash_info(basename, content,
                                                           log_data,
                                                           candidate.info_dir())
        where_to_store_trashed_file = path_of_backup_copy(trash_info_file)

        try:
            self.fs.move(path, where_to_store_trashed_file)
        except IOError as e:
            self.fs.remove_file(trash_info_file)
            raise e
