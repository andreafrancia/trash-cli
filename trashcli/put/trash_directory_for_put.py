import os

from trashcli.put.clock import PutClock
from trashcli.put.info_dir import InfoDir
from trashcli.put.original_location import OriginalLocation
from trashcli.put.real_fs import RealFs
from trashcli.py2compat import url_quote
from trashcli.trash import path_of_backup_copy


class TrashDirectoryForPut:
    def __init__(self,
                 fs,  # type: RealFs
                 info_dir,  # type: InfoDir
                 original_location,  # type: OriginalLocation
                 clock, # type: PutClock
                 ):
        self.fs = fs
        self.info_dir = info_dir
        self.original_location = original_location
        self.clock = clock

    def trash2(self, path, program_name, verbose, path_maker_type, volume,
               info_dir_path):
        path = os.path.normpath(path)

        original_location = self.original_location.for_file(path,
                                                            path_maker_type,
                                                            volume)

        basename = os.path.basename(original_location)
        content = format_trashinfo(original_location, self.clock.now())
        trash_info_file = self.info_dir.persist_trash_info(basename, content,
                                                           program_name,
                                                           verbose,
                                                           info_dir_path)

        where_to_store_trashed_file = path_of_backup_copy(trash_info_file)

        try:
            self.fs.move(path, where_to_store_trashed_file)
        except IOError as e:
            self.fs.remove_file(trash_info_file)
            raise e


def format_trashinfo(original_location, deletion_date):
    content = ("[Trash Info]\n" +
               "Path=%s\n" % format_original_location(original_location) +
               "DeletionDate=%s\n" % format_date(deletion_date)).encode('utf-8')
    return content


def format_date(deletion_date):
    return deletion_date.strftime("%Y-%m-%dT%H:%M:%S")


def format_original_location(original_location):
    return url_quote(original_location, '/')
