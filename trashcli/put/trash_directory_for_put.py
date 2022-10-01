import os

from trashcli.put.path_maker import PathMaker
from trashcli.py2compat import url_quote
from trashcli.trash import path_of_backup_copy


class TrashDirectoryForPut:
    def __init__(self, fs, path_maker, info_dir, original_location):
        self.fs = fs
        self.path_maker = path_maker
        self.info_dir = info_dir
        self.original_location = original_location

    def trash2(self, path, now, program_name, verbose, path_maker_type,
               volume_top_dir, info_dir_path):
        path = os.path.normpath(path)

        original_location = self.path_for_trash_info_for_file(path,
                                                              path_maker_type,
                                                              volume_top_dir)

        basename = os.path.basename(original_location)
        content = format_trashinfo(original_location, now())
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

    def path_for_trash_info_for_file(self, path, path_maker_type,
                                     volume_top_dir):
        path_for_trash_info = self.original_location
        return path_for_trash_info.for_file(path, self.path_maker,
                                            path_maker_type,
                                            volume_top_dir)


def format_trashinfo(original_location, deletion_date):
    content = ("[Trash Info]\n" +
               "Path=%s\n" % format_original_location(original_location) +
               "DeletionDate=%s\n" % format_date(deletion_date)).encode('utf-8')
    return content


def format_date(deletion_date):
    return deletion_date.strftime("%Y-%m-%dT%H:%M:%S")


def format_original_location(original_location):
    return url_quote(original_location, '/')
