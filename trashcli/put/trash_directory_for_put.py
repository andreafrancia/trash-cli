import os

from trashcli.put.clock import PutClock
from trashcli.put.forma_trash_info import format_trashinfo
from trashcli.put.fs import Fs
from trashcli.put.info_dir import InfoDir
from trashcli.put.my_logger import LogData
from trashcli.put.original_location import OriginalLocation
from trashcli.trash import path_of_backup_copy


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
               log_data,  # type: LogData
               path_maker_type,
               volume,
               info_dir_path):
        original_location = self.original_location.for_file(
            path, path_maker_type, volume)
        basename = os.path.basename(original_location)
        content = format_trashinfo(original_location, self.clock.now())
        trash_info_file = self.info_dir.persist_trash_info(basename, content,
                                                           log_data,
                                                           info_dir_path)
        where_to_store_trashed_file = path_of_backup_copy(trash_info_file)

        try:
            self.fs.move(path, where_to_store_trashed_file)
        except IOError as e:
            self.fs.remove_file(trash_info_file)
            raise e
